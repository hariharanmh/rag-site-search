
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
    title = page_data.pop("title") if "title" in page_data else ""
    metadatas = page_data.pop("metadatas") if "metadatas" in page_data else ""

    document = f"URL: {url}\n"
    document += f"Title: {title}\n"

    for header, paragraphs in page_data.items():
        document += f"Header: {header};"
        for p in paragraphs:
            document += f"Paragraph: {p};"
    
    document += f"Metadatas: {metadatas}\n"

    return document