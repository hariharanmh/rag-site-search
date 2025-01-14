from bs4 import BeautifulSoup
import requests
import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def collect_title_headers_paragraphs_meta(soup):
    """
    Collect title, headers, text content, and metadata from HTML content
    Returns a dictionary with structured content
    """
    try:
        page_data = {"title": "", "metadatas": [], "headings": {}}

        # Find title safely
        try:
            if soup and soup.title and soup.title.string:
                page_data["title"] = clean_text(soup.title.string)
        except Exception as e:
            print(f"Error extracting title: {str(e)}")

        # Text-containing elements we want to collect
        text_elements = [
            "p",
            "span",
            "div",
            "li",
            "td",
            "th",
            "a",
            "strong",
            "em",
            "label",
        ]

        # Find all headers h1-h6 and their text content
        try:
            all_headings = []
            for level in range(1, 7):
                headings = soup.find_all(f"h{level}")
                for heading in headings:
                    if heading and heading.text:
                        all_headings.append((level, heading))

            all_headings.sort(
                key=lambda x: x[1].sourceline if hasattr(x[1], "sourceline") else 0
            )

            for idx, (level, heading) in enumerate(all_headings):
                try:
                    header_text = clean_text(heading.text)
                    if not header_text:
                        continue

                    base_header_text = header_text
                    counter = 1
                    while header_text in page_data["headings"]:
                        header_text = f"{base_header_text} ({counter})"
                        counter += 1

                    page_data["headings"][header_text] = {
                        "level": level,
                        "texts": [],  # Changed from paragraphs to texts
                        "position": idx,
                    }

                    # Find next element and collect all text content
                    current_element = heading.find_next_sibling()
                    while current_element:
                        if current_element.name and current_element.name[0] == "h":
                            try:
                                current_level = int(current_element.name[1])
                                if current_level <= level:
                                    break
                            except ValueError:
                                pass

                        # Check if current element is a text container
                        if current_element.name in text_elements:
                            # Get text from the current element
                            element_text = clean_text(current_element.text)
                            if element_text:
                                page_data["headings"][header_text]["texts"].append(
                                    {
                                        "type": current_element.name,
                                        "content": element_text,
                                    }
                                )

                            # Also get text from nested elements
                            for nested in current_element.find_all(text_elements):
                                nested_text = clean_text(nested.text)
                                if nested_text and nested_text != element_text:
                                    page_data["headings"][header_text]["texts"].append(
                                        {"type": nested.name, "content": nested_text}
                                    )

                        current_element = current_element.find_next_sibling()

                except Exception as e:
                    print(
                        f"Error processing heading '{header_text if 'header_text' in locals() else 'unknown'}': {str(e)}"
                    )
                    continue

        except Exception as e:
            print(f"Error processing headings: {str(e)}")
            page_data["headings"] = {}

        # Collect text content not under any heading
        try:
            page_data["orphan_texts"] = []
            for element in soup.find_all(text_elements):
                # Skip if element is under a heading (already collected)
                if not any(heading.find(element) for (level, heading) in all_headings):
                    text = clean_text(element.text)
                    if text:
                        page_data["orphan_texts"].append(
                            {"type": element.name, "content": text}
                        )
        except Exception as e:
            print(f"Error collecting orphan texts: {str(e)}")
            page_data["orphan_texts"] = []

        # Collect metadata safely
        try:
            page_data["metadatas"] = []
            if soup.find_all("meta"):
                for metadata in soup.find_all("meta"):
                    try:
                        content = metadata.get("content", "")
                        if content:
                            cleaned_text = clean_text(content)
                            if cleaned_text:
                                meta_data = {
                                    "content": cleaned_text,
                                    "name": metadata.get("name", ""),
                                    "property": metadata.get("property", ""),
                                }
                                page_data["metadatas"].append(meta_data)
                    except Exception as e:
                        print(f"Error processing metadata item: {str(e)}")
                        continue
        except Exception as e:
            print(f"Error processing metadata: {str(e)}")
            page_data["metadatas"] = []

        return page_data

    except Exception as e:
        print(f"Error in collect_title_headers_paragraphs_meta: {str(e)}")
        return {"title": "", "metadatas": [], "headings": {}, "orphan_texts": []}


def get_urls_from_sitemap(sitemap_url):
    """Extract all URLs from a sitemap"""
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        namespace = root.tag.split("}")[0] + "}"
        urls = []

        if "sitemapindex" in root.tag:
            sitemap_urls = [
                elem.find(f"{namespace}loc").text
                for elem in root.findall(f".//{namespace}sitemap")
            ]
            for url in sitemap_urls:
                urls.extend(get_urls_from_sitemap(url))
        else:
            urls = [
                elem.find(f"{namespace}loc").text
                for elem in root.findall(f".//{namespace}url")
            ]

        return urls

    except Exception as e:
        print(f"Error processing sitemap {sitemap_url}: {str(e)}")
        return []


def scrape_page(url):
    """Scrape a single page and return its data"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        page_data = collect_title_headers_paragraphs_meta(soup)

        return {url: page_data}

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {url: {}}


def scrape_site_from_sitemap(sitemap_url, max_workers=5):
    """
    Scrape entire site using sitemap URL

    Args:
        sitemap_url (str): URL of the sitemap
        max_workers (int): Maximum number of concurrent threads for scraping

    Returns:
        dict: Dictionary with URLs as keys and their content data as values
    """
    print(f"Starting sitemap scraping from: {sitemap_url}")

    urls = get_urls_from_sitemap(sitemap_url)
    print(f"Found {len(urls)} URLs in sitemap")

    site_data = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(scrape_page, url): url for url in urls}

        for future in future_to_url:
            try:
                page_data = future.result()
                site_data.update(page_data)
            except Exception as e:
                print(f"Error processing future: {str(e)}")

    return site_data
