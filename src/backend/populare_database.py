import argparse
import os
import shutil

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
# from langchain_community.vectorstores import Chroma
import chromadb
from pypdf import PdfReader

CHROMA_PATCH = "chroma"
DATA_PATH = "src/backend/resources/test/"

def main():
  # Check if the database should be cleared: if the --reset flag is set, delete the database
  parser = argparse.ArgumentParser()
  parser.add_argument("--reset", action="store_true", help="Reset the database")
  args = parser.parse_args()
  if args.reset:
    print("Resetting the database - a la poubelle! 🗑️")
    reset_database()

  # reader = PdfReader("src/backend/resources/test.pdf")
  # number_of_pages = len(reader.pages)
  # page = reader.pages[0]
  # text = page.extract_text()
  # print(text[:100])
  # Crate or update the data store
  documents = load_documents()
  chunks = split_documents(documents)
  add_to_database(chunks)


def load_documents():
  # Load all documents from the data directory
  loader = PyPDFDirectoryLoader(
    path=DATA_PATH,
    recursive=False,
    mode="page"
  )
  documents = loader.load()
  return documents


def split_documents(documents):
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=75,
    length_function=len,
    is_separator_regex=False
  )
  return text_splitter.split_documents(documents)


def add_to_database(chunks: list[Document]):
  chroma_client = chromadb.HttpClient(host='localhost', port=5432)

  chunks_with_ids = calculate_chunk_ids(chunks)

  # Add or Update the documents.
  collection = chroma_client.get_or_create_collection(name="vorwerk", embedding_function=get_embedding_function())  # IDs are always included by default
  existing_items = collection.get(include=[])
  existing_ids = set(existing_items["ids"])
  print(f"Number of existing documents in DB: {existing_ids}")

  # Only add documents that don't exist in the DB.
  new_chunks = []
  for chunk in chunks_with_ids:
      if chunk.metadata["id"] not in existing_ids:
          new_chunks.append(chunk)

  if len(new_chunks):
      print(f"👉 Adding new documents: {len(new_chunks)}")
      new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
      new_chunk_documents =  [chunk.page_content for chunk in new_chunks]
      new_chunk_metadatas=  [chunk.metadata for chunk in new_chunks]
      collection.add(documents=new_chunk_documents, metadatas=new_chunk_metadatas, ids=new_chunk_ids)
      # print the first 100 characters of each new_chunk.page_content
      # for chunk in new_chunks:
      #   print(chunk.page_content[:100])
      #   print(chunk.metadata)
      #   print(new_chunk_ids)
      
      print(f"👉 Added {len(new_chunks)} new documents")
      # collection.persist()
  else:
      print("✅ No new documents to add")
  

def calculate_chunk_ids(chunks):

    # This will create IDs like "resource/test.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks

if __name__ == "__main__":
    main()