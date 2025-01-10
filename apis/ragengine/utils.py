from collections import OrderedDict

from configs import constants
from .scrape import scrape_site_from_sitemap
from .context_formatters import format_for_llm, format_for_embeddings


def create_knowledge_base_from_sitemap(brain, sitemap_url: str, VECTOR_DB):
    site_data = scrape_site_from_sitemap(sitemap_url)

    print("Site scraped successfully")

    docs = []
    for url, page_data in site_data.items():
        llm_context, embedding_chunks = format_for_llm(page_data), format_for_embeddings(page_data)
        docs.append((llm_context, embedding_chunks))

    print(f"Scraped {len(docs)} pages")

    VECTOR_DB["url"] = sitemap_url
    data, embeddings = OrderedDict(), []

    last_idx = 0
    for (llm_context, embedding_chunks) in docs:
        embedding_chunks_size = len(embedding_chunks)
        data[f"{last_idx}-{last_idx+embedding_chunks_size}"] = llm_context
        embeddings.extend(embedding_chunks)
        last_idx += (embedding_chunks_size + 1)

    VECTOR_DB["data"], VECTOR_DB["embedding"] = data, brain.generate_embeddings(embeddings)

    print(f"Created knowledge base with {len(VECTOR_DB['data'])} documents")
    print(f"Created knowledge base with {len(VECTOR_DB['embedding'])} embeddings")