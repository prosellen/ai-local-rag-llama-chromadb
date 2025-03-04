import argparse
import os
import shutil
import logging
from pathlib import Path

from docling.datamodel.document import DoclingDocument, DocItem
from docling.chunking import HybridChunker, DocChunk, DocMeta
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, ConversionResult
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from transformers import AutoTokenizer

from chromadb.utils import embedding_functions


from get_embedding_function import get_embedding_function
# from langchain_community.vectorstores import Chroma
import chromadb
from pypdf import PdfReader

CHROMA_PATCH = "chroma"
DATA_PATH = "src/backend/resources/test/"
OUT_PATH = "src/backend/resources/scratch"
EMBED_MODEL_ID="sentence-transformers/all-MiniLM-L6-v2"

_log = logging.getLogger(__name__)

def main():
  # Check if the database should be cleared: if the --reset flag is set, delete the database
  parser = argparse.ArgumentParser()
  parser.add_argument("--reset", action="store_true", help="Reset the database")
  args = parser.parse_args()
  if args.reset:
    print("Resetting the database - a la poubelle! 🗑️")
    reset_database()

  document_list = create_document_list()
  converted_documents = convert_documents(document_list)
  chunked_documents = chunk_documents(converted_documents)
  add_to_database(chunked_documents)


def create_document_list() -> list[str]:
  # Create a list of documents from the data directory
  document_list = []
  for root, dirs, files in os.walk(DATA_PATH):
    for file in files:
      if file.endswith((".pdf", ".docx", ".pptx", ".xlsx", ".txt")):
        document_list.append(os.path.join(root, file))
  return document_list



def convert_documents(document_list: list[str]) -> list[ConversionResult]:
  doc_converter = DocumentConverter()
  converted_documents = doc_converter.convert_all(document_list)

  # # Save the converted documents to the data directory
  # save_documents(converted_documents)

  return converted_documents

def save_documents(documents):
  # Save the documents to the data directory
  for res in documents:
    out_path = Path(OUT_PATH)
    out_path.mkdir(parents=True, exist_ok=True)
    _log.debug(res.document._export_to_indented_text(max_text_len=16))
    # Export Docling document format to markdowndoc:
    with (out_path / f"{res.input.file.stem}.md").open("w") as fp:
      fp.write(res.document.export_to_markdown())


def chunk_documents(conversion_results: list[ConversionResult]) -> list[any]:
  # Iterate over all the documents in the list
  document_chunks = []

  tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL_ID);
  MAX_TOKEN=512

  for conversion_result in conversion_results:
    chunker = HybridChunker(
       tokenizer=tokenizer,
       max_tokens=MAX_TOKEN,
       merge_peers=True,
    )
    chunk_iter = chunker.chunk(dl_doc=conversion_result.document)
    for i, chunk in enumerate(chunk_iter):
      # chunk.metadata["id"] = f"{document.input.file.stem}:{chunk.metadata['page']}:{i}"
      document_chunks.append(chunk)
  return document_chunks

def add_to_database(chunks: list[DocChunk]): 
  chroma_client = chromadb.HttpClient(host='localhost', port=5432)

  # Add or Update the documents.
  collection = chroma_client.get_or_create_collection(name="vorwerk", embedding_function=embedding_functions.DefaultEmbeddingFunction())  # IDs are always included by default
  existing_items = collection.get(include=[])
  existing_ids = set(existing_items["ids"])
  print(f"Number of existing documents in DB: {existing_ids}")

  # Only add documents that don't exist in the DB.


  if len(chunks):
      print(f"👉 Adding new documents: {len(chunks)}")
      new_chunk_ids = create_unique_chunk_id(chunks)
      new_chunk_documents = [chunk.text for chunk in chunks]
      new_chunk_metadatas = create_meta_data(chunks)
      collection.add(documents=new_chunk_documents, metadatas=new_chunk_metadatas, ids=new_chunk_ids)
      # print the first 100 characters of each new_chunk.page_content

      print(f"👉 Added {len(chunks)} new documents")
      # collection.persist()
  else:
      print("✅ No new documents to add")

def create_meta_data(chunks: list[DocMeta]) -> DocMeta:
  # loop over the chunks
  # for each chunk, create a dictionary with the following keys:
  # - origin: filename
  # - uri: path to the file
  # - binary_hash: hash of the binary file
  # store the dictionary in a list
  # return the list
  meta_data_list = []
  for chunk in chunks:
    meta_data = {
      "origin": chunk.meta.origin.filename,
      "uri": chunk.meta.origin.uri or '',
      "binary_hash": chunk.meta.origin.binary_hash
    }
    meta_data_list.append(meta_data)
  return meta_data_list


def create_unique_chunk_id(chunks:list[DocChunk]) -> str:
  chunk_ids = []
  for i, chunk in enumerate(chunks):
    chunk_ids.append(f"{chunk.meta.origin.filename}:{i}")
  return chunk_ids

if __name__ == "__main__":
    main()