import argparse
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
import chromadb

from ollama import Client
from ollama import ChatResponse

from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    # query_text = "What are the main change dimensions?"
    query_rag(query_text)


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    chroma_client = chromadb.HttpClient(host='localhost', port=5432)
    db = chroma_client.get_collection(name="vorwerk", embedding_function=get_embedding_function())


    # Search the DB.
    results = db.query(query_texts=query_text, n_results=5)

    context_text = "\n\n---\n\n".join(doc[0] for doc in results['documents'])
    # print(context_text)
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    client = Client(
      host='http://localhost:11434'
    )

    response = client.chat(model='mistral', messages=[
      {
        'role': 'user',
        'content': prompt,
      },
    ])
    response_text = response.message.content

    # sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\n" # Sources: {sources}"
    print(formatted_response)
    return response_text


if __name__ == "__main__":
    main()
