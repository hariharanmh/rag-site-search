import pickle
from collections import OrderedDict

from configs import constants
from .scrape import scrape_site_from_sitemap
from .context_formatters import format_for_llm, format_for_embeddings


def create_knowledge_base_from_sitemap(brain, sitemap_url: str, db):
    site_data = scrape_site_from_sitemap(sitemap_url)

    print("Site scraped successfully")

    docs = []
    for _, page_data in site_data.items():
        llm_context, embedding_chunks = format_for_llm(
            page_data
        ), format_for_embeddings(page_data)
        docs.append((llm_context, embedding_chunks))

    print(f"Scraped {len(docs)} pages")

    db["url"] = sitemap_url
    data, embeddings = OrderedDict(), []

    last_idx = 0
    for llm_context, embedding_chunks in docs:
        embedding_chunks_size = len(embedding_chunks)
        data[f"{last_idx}-{last_idx+embedding_chunks_size}"] = llm_context
        embeddings.extend(embedding_chunks)
        last_idx += embedding_chunks_size + 1

    db["data"], db["embedding"] = data, brain.generate_embeddings(
        documents=embeddings, use_multi_process=True
    )
    db["status"] = "completed"

    print(f"Created knowledge base with {len(db['data'])} documents")
    print(f"Created knowledge base with {len(db['embedding'])} embeddings")


def load_vector_db_from_pickle_file(
    db: dict, file_path: str = constants.VECTOR_DB_FILE
):
    with open(file_path, "rb") as pickle_file:
        loaded_db = pickle.load(pickle_file)
        db.clear()
        db.update(loaded_db)

    print("Size of loaded vector db:", len(db["data"]) if "data" in db else 0)


def store_vector_db_in_pickle_file(db: dict, file_path: str = constants.VECTOR_DB_FILE):
    with open(file_path, "wb") as pickle_file:
        pickle.dump(db, pickle_file)

    print("Stored vector db in pickle file")