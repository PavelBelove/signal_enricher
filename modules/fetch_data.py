import requests
import pandas as pd
import time
import xml.etree.ElementTree as ET
import httpx
from requests.exceptions import RequestException
from newspaper import Article
from config.api_keys import api_keys
from modules.date_utils import parse_date

# import ssl
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException
import time
from datetime import datetime, timedelta



# API data
user = api_keys["xmlstock_user"]
key = api_keys["xmlstock_key"]
url = "https://xmlstock.com/google/xml/"

def fetch_xmlstock_search_results(query, days=30, num_results=100, num_pages=1, sites=None, verbose=False):
    """
    Fetch search results from XMLStock API.

    Args:
        query (str): Search query string.
        days (int): Number of days to look back from the current date.
        num_results (int): Number of results to fetch per page.
        num_pages (int): Number of pages to fetch.
        sites (list): List of sites to search in.
        verbose (bool): Flag to enable/disable verbose output.

    Returns:
        list: List of search results with title, link, and publication date.
    """
    if sites is None or not sites:
        sites = [""]
    
    results = []
    for site in sites:
        site_query = f"{query} site:{site}" if site else query
        if verbose:
            print(f"Searching with query: {site_query}")
        
        params = {
            "user": user,
            "key": key,
            "query": site_query,
            "num": num_results,
            "date": (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            "sort": "date"
        }
        if verbose:
            print("Fetching results with params:", params)
        
        for page in range(1, num_pages + 1):
            params['page'] = page
            try:
                response = requests.get(url, params=params, timeout=10)
                if verbose:
                    print("Response status code:", response.status_code)
                if response.status_code != 200:
                    if verbose:
                        print(f"Error fetching results: {response.status_code}")
                        print(response.text)
                    continue

                try:
                    if verbose:
                        print("Response content:", response.content)
                    root = ET.fromstring(response.content)
                    for group in root.findall('.//group'):
                        for doc in group.findall('doc'):
                            pub_date = doc.find('pubDate').text if doc.find('pubDate') is not None else "N/A"
                            pub_date_dt = parse_date(pub_date) if pub_date != "N/A" else None
                            if pub_date_dt is None or pub_date_dt >= (datetime.now() - timedelta(days=days)):
                                result = {
                                    'title': doc.find('title').text if doc.find('title') is not None else "N/A",
                                    'link': doc.find('url').text if doc.find('url') is not None else "N/A",
                                    'pubDate': pub_date
                                }
                                results.append(result)
                    if verbose:
                        print(f"Parsed results for {site}: {len(results)}")
                except ET.ParseError as e:
                    if verbose:
                        print(f"Error parsing XML response: {e}")
            except requests.exceptions.RequestException as e:
                if verbose:
                    print(f"Error fetching results: {e}")

    return results

# def fetch_and_parse(url, verbose=False):
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.126 Safari/537.36")

#     service = Service('/usr/local/bin/chromedriver')  # Убедитесь, что путь правильный

#     try:
#         with webdriver.Chrome(service=service, options=options) as driver:
#             driver.get(url)
#             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(2)

#             title = driver.title
#             content = driver.find_element(By.TAG_NAME, "body").text

#             return {
#                 'title': title,
#                 'authors': [],
#                 'text': content,
#                 'article_url': url
#             }
#     except TimeoutException:
#         print(f"Timeout while loading page: {url}")
#         return {'title': "N/A", 'authors': [], 'text': f"Error: Timeout while loading page", 'article_url': url}
#     except WebDriverException as e:
#         print(f"WebDriver error for {url}: {e}")
#         return {'title': "N/A", 'authors': [], 'text': f"Error: WebDriver error - {str(e)}", 'article_url': url}
#     except Exception as e:
#         print(f"Error parsing article: {url}\n{e}")
#         return {'title': "N/A", 'authors': [], 'text': f"Error parsing: {str(e)}", 'article_url': url}

def fetch_and_parse(url, verbose=False):
    """
    Fetch and parse an article from a given URL.

    Args:
        url (str): URL of the article to fetch and parse.
        verbose (bool): Flag to enable/disable verbose output.

    Returns:
        dict: Dictionary containing the article's title, authors, text, and URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        article = Article(url)
        article.set_html(response.text)
        article.parse()
        return {
            'title': article.title,
            'authors': article.authors,
            'text': article.text,
            'article_url': url
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article: {url}\n{e}")
        return {
            'title': "N/A",
            'authors': [],
            'text': f"Error fetching: {str(e)}",
            'article_url': url
        }
    except Exception as e:
        print(f"Error parsing article: {url}\n{e}")
        return {
            'title': "N/A",
            'authors': [],
            'text': f"Error parsing: {str(e)}",
            'article_url': url
        }

def save_results_to_csv(results, output_filename, verbose=False):
    """
    Save search results to a CSV file.

    Args:
        results (list): List of search results to save.
        output_filename (str): Path to the output CSV file.
        verbose (bool): Flag to enable/disable verbose output.
    """
    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_filename, index=False)
        if verbose:
            print(f"Extracted articles saved to '{output_filename}'")
    else:
        if verbose:
            print("No articles were extracted.")