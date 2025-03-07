import argparse
from string import Template

import chromadb

from openai import OpenAI

from get_embedding_function import get_embedding_function

CHROMA_PATH = "src/chromadb/local"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

${context}

---

Answer the question based on the above context: ${question}
"""


def main():
    # Create CLI.
    # parser = argparse.ArgumentParser()
    # parser.add_argument("query_text", type=str, help="The query text.")
    # args = parser.parse_args()
    # query_text = args.query_text
    query_text = "What are the main change dimensions?"
    query_rag(query_text)


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    # chroma_client = chromadb.HttpClient(host='localhost', port=5432)
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_collection(name="vorwerk", embedding_function=get_embedding_function())

    # Search the DB.
    results = collection.query(query_texts=query_text, n_results=5)

    context_text = "\n\n---\n\n".join(doc[0] for doc in results['documents'])
    # print(context_text)
    prompt_template = Template(PROMPT_TEMPLATE)
    prompt = prompt_template.substitute(context=context_text, question=query_text)
    # print(prompt)

    # llm_client = Client(
    #   # host='http://localhost:11434' // Ollama
    #   host='http://localhost:1234/v1' # LM Studio
    # )
    openai_client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    response = openai_client.chat.completions.create(
      model='gemma-2-2b-it', 
      messages=[
        {
          'role': 'user',
          'content': prompt,
        }
      ],
      temperature=0.7,
    )
    response_text = response.choices[0].message.content

    # sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\n" # Sources: {sources}"
    print(formatted_response)
    return response_text


if __name__ == "__main__":
    main()
