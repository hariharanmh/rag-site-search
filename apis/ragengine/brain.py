import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

class Brain:

    def __init__(self, embedding_model_name: str = "Alibaba-NLP/gte-base-en-v1.5"):
        self.embed_model = SentenceTransformer(embedding_model_name, trust_remote_code=True)
        genai.configure(api_key=userdata.get("GOOGLE_API_KEY"))
        print(f"Loaded embedding model: {embedding_model_name}")

    def generate_embeddings(embed_model, documents: list[str]) -> list[list[float]]:
        embeddings = embed_model.encode(documents, normalize_embeddings=True)
        print(f"Generated embeddings for {len(documents)} documents with size {embeddings.size}")
        return embeddings

    def get_top_k_matching_docs(docs, dosc_embedding, query_embedding, k: int = 3):
        scores = np.dot(query_embed, docs_embed.T)
        top_k_ids = np.argsort(scores.flatten())[::-1][:k]
        most_scored_docs = [docs[idx] for idx in top_k_ids]
        return most_scored_docs

    def get_context(query: str, ) -> str:
        most_scored_docs = get_top_k_matching_docs(docs, docs_embed, query_embed)
        context = ""
        for doc in most_scored_docs:
            context += f"{doc}\n"
        return context

    def generate_response(query: str, context: str) -> str:
        prompt = f"""
            Use the following CONTEXT to answer the QUESTION at the end.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.

            CONTEXT: {CONTEXT}
            QUESTION: {query}
        """
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
