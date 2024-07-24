import requests
import pandas as pd
import time
import xml.etree.ElementTree as ET
import httpx
from requests.exceptions import RequestException
from newspaper import Article
from config.api_keys import api_keys
from modules.date_utils import parse_date
from datetime import datetime, timedelta

# API data
user = api_keys["xmlstock_user"]
key = api_keys["xmlstock_key"]
url = "https://xmlstock.com/google/xml/"

def fetch_xmlstock_search_results(query, days=30, num_results=100, num_pages=1, sites=None, verbose=False):
    if sites is None or not sites:
        sites = [""]
    
    results = []
    for site in sites:
        site_query = f"{query} site:{site}" if site else query
        if verbose:
            print(f"Поиск с запросом: {site_query}")
        
        params = {
            "user": user,
            "key": key,
            "query": site_query,
            "num": num_results,
            "date": (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            "sort": "date"
        }
        if verbose:
            print("Отправка запроса с параметрами:", params)
        
        for page in range(1, num_pages + 1):
            params['page'] = page
            try:
                response = requests.get(url, params=params, timeout=10)
                if verbose:
                    print("Код статуса ответа:", response.status_code)
                    print("URL запроса:", response.url)
                    print("Заголовки ответа:", response.headers)
                    print("Содержимое ответа:", response.text[:500])  # Выводим первые 500 символов ответа
                if response.status_code != 200:
                    if verbose:
                        print(f"Ошибка при получении результатов: {response.status_code}")
                        print(response.text)
                    continue

                try:
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
                        print(f"Обработано результатов для {site}: {len(results)}")
                except ET.ParseError as e:
                    if verbose:
                        print(f"Ошибка при разборе XML ответа: {e}")
                        print("Содержимое ответа:", response.text)
            except requests.exceptions.RequestException as e:
                if verbose:
                    print(f"Ошибка при получении результатов: {e}")

    return results

def fetch_and_parse(url, verbose=False, proxy=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
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
    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_filename, index=False)
        if verbose:
            print(f"Extracted articles saved to '{output_filename}'")
    else:
        if verbose:
            print("No articles were extracted.")