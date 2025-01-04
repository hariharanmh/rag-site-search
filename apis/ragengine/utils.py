
from .routes import brain
from .scrape import scrape_site_from_sitemap

import json

VECTOR_DB = {}

def create_knowledge_base_from_sitemap(sitemap_url: str):
    site_data = scrape_site_from_sitemap(sitemap_url)

    docs = []
    for url, page_data in site_data.items():
        docs = create_document_from_page_data(url, page_data)
    
    VECTOR_DB["url"] = sitemap_url
    VECTOR_DB["data"] = docs
    VECTOR_DB["embedding"] = brain.generate_embeddings(docs)

    # with open('data.json', 'w') as f:
    #     json.dump(site_data, f)

    # print(f"Scraped {len(site_data)} pages")
    
    # for url, page_data in site_data.items():
    #     print(f"\nURL: {url}")
    #     print(f"Title: {page_data['title']}")
    #     for header, paragraphs in page_data.items():
    #         print(f"\nHeader: {header}")
    #         print("Paragraphs:")
    #         for p in paragraphs:
    #             print(f"- {p[:100]}...")
    #     print(f"Metadatas: {page_data['metadatas']}")


def create_document_from_page_data(url: str, page_data: dict) -> str:
    
    document = f"URL: {url}\n"
    document += f"Title: {page_data['title']}\n"

    for header, paragraphs in page_data.items():
        document += f"Header: {header};"
        for p in paragraphs:
            document += f"Paragraph: {p};"

    return document