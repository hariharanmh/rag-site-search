import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from configs.constants import GEMINI_API_KEY

class Brain:

    def __init__(self, embedding_model_name: str = "Alibaba-NLP/gte-base-en-v1.5"):
        self.embed_model = SentenceTransformer(embedding_model_name, trust_remote_code=True)
        genai.configure(api_key=GEMINI_API_KEY)
        print(f"Loaded embedding model: {embedding_model_name}")

    def generate_embeddings(self, documents: list[str]) -> list[list[float]]:
        embeddings = self.embed_model.encode(documents, normalize_embeddings=True)
        print(f"Generated embeddings for {len(documents)} documents with size {embeddings.size}")
        return embeddings

    def get_top_k_matching_docs(self, docs_embedding, query_embedding, k: int = 3) -> list[int]:
        scores = np.dot(query_embedding, docs_embedding.T)
        top_k_ids = np.argsort(scores.flatten())[::-1][:k]
        return top_k_ids

    def get_context(self, query, docs, docs_embedding, query_embedding) -> str:
        top_k_ids = self.get_top_k_matching_docs(docs_embedding, query_embedding,)
        most_scored_docs = [docs[idx] for idx in top_k_ids]
        context = ""
        for doc in most_scored_docs:
            context += f"{doc}\n"
        return context

    def generate_response(self, query: str, VECTOR_DB) -> str:
        docs = VECTOR_DB["data"]
        docs_embedding = VECTOR_DB["embedding"]
        query_embedding = self.embed_model.encode([query], normalize_embeddings=True)
        context = self.get_context(query, docs, docs_embedding, query_embedding)
        prompt = f"""
            You are an intelligent search engine. You will be provided with some retrieved context, as well as the users query.

            Your job is to understand the request, and answer based on the retrieved context.
            Here is context:

            <context>
            {context}
            </context>

            Question: {query}
        """
        print(prompt)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
