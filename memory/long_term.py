import chromadb

class LongTermMemory:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self._model_name = model_name
        self.chroma_client = ChromaDB