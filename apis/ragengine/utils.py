
from configs import constants
from .scrape import scrape_site_from_sitemap


def create_knowledge_base_from_sitemap(brain, sitemap_url: str, VECTOR_DB):
    site_data = scrape_site_from_sitemap(sitemap_url)

    docs = []
    for url, page_data in site_data.items():
        docs.append(create_document_from_page_data(url, page_data))

    print(f"Scraped {len(docs)} pages")
    
    VECTOR_DB["url"] = sitemap_url
    VECTOR_DB["data"] = docs
    VECTOR_DB["embedding"] = brain.generate_embeddings(docs)


def create_document_from_page_data(url: str, page_data: dict) -> str:
    document = f"URL: {url}\n"
    document += f"Title: {page_data.get('title', )}\n"

    document += "Headings and their paragraphs:\n"
    for heading, content in page_data.get('headings', {}).items():
        document += f"{heading}\n"
        paragraphs = content['paragraphs']
        if paragraphs:
            document += f"{' '.join(paragraphs)}\n"
    
    document += f"Metadatas:"
    for metadata in page_data.get("metadatas", []):
        document += f"{metadata['content']}\n"

    return document