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
    page_data["title"] = clean_text(soup.title.string)

    # Find all h1 headers
    headings = soup.find_all('h1')
    
    for heading in headings:
        header_text = clean_text(heading.text)
        
        page_data[header_text] = []
        
        current_element = heading.find_next_sibling()
        while current_element and current_element.name != 'h1':
            if current_element.name == 'p':
                paragraph_text = clean_text(current_element.text)
                page_data[header_text].append(paragraph_text)
            current_element = current_element.find_next_sibling()
    
    page_data["metadatas"] = []
    for metadata in soup.find_all('meta'):
        cleaned_text = clean_text(metadata.text)
        if cleaned_text and cleaned_text.strip() != "":
            page_data["metadatas"].append(cleaned_text)

    return page_data

def get_urls_from_sitemap(sitemap_url):
    """Extract all URLs from a sitemap"""
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
        
        # Handle both XML sitemaps and sitemap indexes
        root = ET.fromstring(response.content)
        
        # Remove namespace for easier parsing
        namespace = root.tag.split('}')[0] + '}'
        urls = []
        
        # Check if it's a sitemap index
        if 'sitemapindex' in root.tag:
            # Get URLs of all sitemaps
            sitemap_urls = [elem.find(f'{namespace}loc').text 
                          for elem in root.findall(f'.//{namespace}sitemap')]
            
            # Recursively process each sitemap
            for url in sitemap_urls:
                urls.extend(get_urls_from_sitemap(url))
        else:
            # Regular sitemap
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
        dict: Dictionary with URLs as keys and their header-paragraph data as values
    """
    print(f"Starting sitemap scraping from: {sitemap_url}")
    
    # Get all URLs from sitemap
    urls = get_urls_from_sitemap(sitemap_url)
    print(f"Found {len(urls)} URLs in sitemap")
    
    # Scrape all pages concurrently
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