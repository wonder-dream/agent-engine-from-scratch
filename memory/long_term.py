import chromadb
from sentence_transformers import SentenceTransformer


class LongTermMemory:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="long_term_memory")

    async def store(self, facts: list[str]) -> None:
        if not facts:
            return

        embeddings = self.model.encode(facts).tolist()
        ids = [f"fact_{hash(fact) % 10**10}" for fact in facts]

        self.collection.add(
            embeddings=embeddings,
            documents=facts,
            ids=ids,
        )

    async def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        if self.collection.count() == 0:
            return []

        query_embeddings = self.model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=top_k,
        )

        docs = results["documents"]
        return docs[0] if docs else []
