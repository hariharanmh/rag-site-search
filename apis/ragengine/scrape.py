from bs4 import BeautifulSoup
import requests
import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def collect_title_headers_paragraphs_meta(soup):
    """
    Collect headers and their associated paragraphs from HTML content
    Returns a dictionary with headers as keys and lists of paragraphs as values
    """
    page_data = {}
    # Find title
    if soup.title:
        page_data["title"] = clean_text(soup.title.string)

    # Find all headers h1-h6
    for level in range(1, 7):
        headings = soup.find_all(f'h{level}')
        for heading in headings:
            header_text = clean_text(heading.text)
            if header_text:
                if header_text not in page_data["headings"]:
                    page_data["headings"][header_text] = {
                        "level": level,
                        "paragraphs": [],
                        "position": len(page_data["headings"])
                    }
                
                # Collect paragraphs until next heading of same or higher level
                current_element = heading.find_next_sibling()
                while current_element:
                    if current_element.name and current_element.name[0] == 'h':
                        current_level = int(current_element.name[1])
                        if current_level <= level:
                            break
                    if current_element.name == 'p':
                        paragraph_text = clean_text(current_element.text)
                        if paragraph_text:
                            page_data["headings"][header_text]["paragraphs"].append(paragraph_text)
                    current_element = current_element.find_next_sibling()

    # Collect metadata
    page_data["metadatas"] = []
    for metadata in soup.find_all('meta'):
        if metadata.get('content'):
            cleaned_text = clean_text(metadata['content'])
            metadata_name = metadata.get('name', '')
            if cleaned_text and metadata_name == 'description':
                meta_data = {
                    'content': cleaned_text,
                    'name': metadata_name,
                    'property': metadata.get('property', ''),
                }
                page_data["metadatas"].append(meta_data)

    return page_data

def get_urls_from_sitemap(sitemap_url):
    """Extract all URLs from a sitemap"""
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        namespace = root.tag.split('}')[0] + '}'
        urls = []
        
        if 'sitemapindex' in root.tag:
            sitemap_urls = [elem.find(f'{namespace}loc').text 
                          for elem in root.findall(f'.//{namespace}sitemap')]
            for url in sitemap_urls:
                urls.extend(get_urls_from_sitemap(url))
        else:
            urls = [elem.find(f'{namespace}loc').text 
                   for elem in root.findall(f'.//{namespace}url')]
        
        return urls
        
    except Exception as e:
        print(f"Error processing sitemap {sitemap_url}: {str(e)}")
        return []

def scrape_page(url):
    """Scrape a single page and return its data"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
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