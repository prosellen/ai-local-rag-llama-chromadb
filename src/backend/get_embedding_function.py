from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)


def get_embedding_function():
  ollama_ef = OllamaEmbeddingFunction(
      url="http://localhost:11434/api/embeddings",
      model_name="nomic-embed-text",
  )

  return ollama_ef
