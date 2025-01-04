
# import polars as pl
from .scrape import scrape_site_from_sitemap
# from .chroma_utils import build_chroma_collection

from configs import constants
# from .routes import VECTOR_DB

def create_knowledge_base_from_sitemap(brain, sitemap_url: str, VECTOR_DB):
    site_data = scrape_site_from_sitemap(sitemap_url)

    docs = []
    for url, page_data in site_data.items():
        docs.append(create_document_from_page_data(url, page_data))

    print("="*100)
    print(f"Scraped {len(docs)} pages")
    # print(docs)

    VECTOR_DB["url"] = sitemap_url
    VECTOR_DB["data"] = docs
    VECTOR_DB["embedding"] = brain.generate_embeddings(docs)

    print(len(VECTOR_DB.get("data")))
    print(len(VECTOR_DB.get("embedding")))

    # build_chroma_collection(
    #     constants.CHROMA_PATH,
    #     constants.COLLECTION_NAME,
    #     constants.EMBEDDING_MODEL_NAME,
    #     chroma_car_reviews_dict["ids"],
    #     chroma_car_reviews_dict["documents"],
    #     chroma_car_reviews_dict["metadatas"]
    # )

    # with open('data.json', 'w', encoding='utf-8') as f:
    #     json.dump(site_data, f, ensure_ascii=False, indent=4)
    # # print(site_data)
    # with open('sample-data.txt', 'w', encoding='utf-8') as f:
    #     f.write(str(site_data))

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