from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from chromadb.utils import embedding_functions






def get_embedding_function():
  # ollama_ef = OllamaEmbeddingFunction(
  #     url="http://localhost:11434/api/embeddings",
  #     model_name="text-embedding-nomic-embed-text-v1.5",
  # )
  default_embedding_function = embedding_functions.DefaultEmbeddingFunction()

  return default_embedding_function
