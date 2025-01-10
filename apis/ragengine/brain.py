import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from configs.constants import GEMINI_API_KEY

class Brain:

    def __init__(self, embedding_model_name: str = "BAAI/bge-small-en-v1.5"):
        self.embed_model = SentenceTransformer(embedding_model_name, trust_remote_code=True)
        genai.configure(api_key=GEMINI_API_KEY)
        print(f"Loaded embedding model: {embedding_model_name}")

    def generate_embeddings(self, documents: list[str]) -> list[list[float]]:
        embeddings = self.embed_model.encode(documents, normalize_embeddings=True, show_progress_bar=True)
        print(f"Generated embeddings for {len(documents)} documents with size {embeddings.size}")
        return embeddings

    def get_top_k_matching_docs(self, docs, docs_embedding, query_embedding, k: int = 3) -> list[int]:

        def bin_search_on_docs_embedding(target):
            keys = docs.keys()
            
            left, right = 0, len(keys) - 1
            
            while left <= right:
                mid = (left + right) // 2
                start, end = keys[mid].split('-')
                start, end = int(start), int(end)

                if end < target:
                    left = mid + 1
                elif start > target:
                    right = mid - 1
                else:
                    return keys[mid]
            return keys[left]

        scores = np.dot(query_embedding, docs_embedding.T)
        top_k_doc_keys = set()
        for ids in np.argsort(scores.flatten())[::-1]:
            if len(top_k_doc_keys) == k:
                break
            top_k_doc_keys.add(bin_search_on_docs_embedding(ids))

        return top_k_doc_keys

    def get_context(self, query, docs, docs_embedding, query_embedding) -> str:
        top_k_doc_keys = self.get_top_k_matching_docs(docs, docs_embedding, query_embedding,)
        most_scored_docs = [docs[keys] for keys in top_k_doc_keys]
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
        if response.error:
            raise Exception(response.error)
        return response.text
