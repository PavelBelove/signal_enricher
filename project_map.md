# Комментарии для LLM отсутствуют

# Карта проекта

## Инструкция для ИИ

Этот документ представляет собой карту проекта, сгенерированную автоматически. Он содержит структуру проекта, информацию об окружении, граф импортов и содержимое ключевых файлов. Используйте эту информацию для понимания общей архитектуры проекта, его компонентов и их взаимосвязей.

Как использовать эту карту:
1. Изучите структуру проекта для понимания организации файлов и директорий.
2. Обратите внимание на информацию об окружении для учета особенностей системы.
3. Используйте граф импортов для анализа зависимостей между модулями.
4. Изучите содержимое ключевых файлов для понимания их функциональности.
5. Учитывайте комментарии и описания, предоставленные разработчиком.

При работе с проектом основывайтесь на информации из этой карты, но помните, что она может быть неполной или устаревшей. Всегда уточняйте детали у разработчика при необходимости.

## Информация об окружении

- **os**: Linux
- **python_version**: 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0]
- **platform**: Linux-6.5.0-41-generic-x86_64-with-glibc2.35

## Структура проекта (глубина: 3)

```
Signal enricher/
    requirements.txt
    main.py
    conftest.py
    test_gemeny.py
    generate_markdown_map.py
    results/
        designers/
            roles/
                prompt.txt
                search_query.json
            2024-06-13/
            2024-06-14/
            2024-07-02/
            2024-07-03/
        LC/
            roles/
                prompt.txt
                search_query.json
            2024-06-13/
            2024-06-14/
        example_task/
            roles/
                prompt.txt
                search_query.json
    config/
        api_keys.py
        __init__.py
        search_config.json
        new_client_profile.json
        api_keys_example.py
        __pycache__/
    modules/
        fetch_data.py
        clean_data.py
        utils.py
        analyse_data.py
        __init__.py
        client_management.py
        date_utils.py
        __pycache__/
    tests/
        test_fetch_data.py
        test_date_utils.py
        test_utils.py
        test_clean_data.py
        __pycache__/
    .pytest_cache/
        README.md
        v/
            cache/
    __pycache__/
    .git/
        branches/
        hooks/
        info/
        refs/
            heads/
            tags/
            remotes/
        objects/
            pack/
            info/
            0a/
            db/
            f9/
            e5/
            32/
            00/
            ee/
            b8/
            fa/
        logs/
            refs/
```

## Граф импортов

- **main**
- **conftest**
- **test_gemeny**
- **generate_markdown_map**
- **config.api_keys**
- **config.__init__**
- **config.api_keys_example**
- **modules.fetch_data**
  - config.api_keys
- **modules.clean_data**
- **modules.utils**
  - config.api_keys
- **modules.analyse_data**
  - modules.utils
- **modules.__init__**
- **modules.client_management**
- **modules.date_utils**
- **tests.test_fetch_data**
  - modules.fetch_data
- **tests.test_date_utils**
  - modules.date_utils
- **tests.test_utils**
  - modules.utils
- **tests.test_clean_data**
  - modules.clean_data

## Содержимое файлов

### requirements.txt

Описание: beautifulsoup4==4.12.3

```
beautifulsoup4==4.12.3
certifi==2024.2.2
charset-normalizer==3.3.2
fuzzywuzzy==0.18.0
lxml==5.2.1
newspaper3k==0.2.8
nltk==3.8.1
openai==0.28.1
openpyxl==3.1.2
pandas==2.2.2
python-dateutil==2.9.0.post0
python-Levenshtein==0.25.1
rapidfuzz==3.8.1
regex==2024.4.16
requests==2.31.0
six==1.16.0
soupsieve==2.5
tqdm==4.66.2
lxml_html_clean==0.1.1
```

### main.py

Описание: import os

```
import os
import json
import argparse
from datetime import datetime
from modules.fetch_data import fetch_xmlstock_search_results, fetch_and_parse, save_results_to_csv
from modules.clean_data import clean_data
from modules.analyse_data import analyse_data
from modules.client_management import get_client_and_date
import time
import pandas as pd

def fetch_data(client_name, days, num_results, num_pages, queries, exclude, sites, verbose):
    print("Starting data fetching and processing...")
    # Fetch and process data
    all_articles = []
    for query in queries:
        print(f"Fetching data for query: {query}")
        search_results = fetch_xmlstock_search_results(query, days, num_results, num_pages, sites, verbose)
        print(f"Received {len(search_results)} results for query: {query}")
        for result in search_results:
            article_data = fetch_and_parse(result['link'])
            if article_data['title'] != "N/A":
                result.update({
                    'description': article_data['text'],
                    'query': query
                })
                all_articles.append(result)
        time.sleep(2)  # Add delay between requests

    print(f"Total articles fetched: {len(all_articles)}")

    # Save results to CSV
    search_date_str = datetime.now().strftime('%Y-%m-%d')
    current_search_dir = os.path.join('results', client_name, search_date_str)
    os.makedirs(current_search_dir, exist_ok=True)
    results_file = os.path.join(current_search_dir, 'search_results.csv')
    
    if len(all_articles) > 0:
        save_results_to_csv(all_articles, results_file)
        print(f"Results saved to {results_file}")
    else:
        print("No articles were fetched. The results file was not created.")

    return len(all_articles) > 0

def clean_data_only(client_name, verbose):
    search_date_str = datetime.now().strftime('%Y-%m-%d')
    current_search_dir = os.path.join('results', client_name, search_date_str)
    results_file = os.path.join(current_search_dir, 'search_results.csv')

    if not os.path.exists(results_file):
        print(f"Error: Results file not found: {results_file}")
        print("Please make sure to run data fetching before cleaning.")
        return

    # Check if the results file is empty before calling clean_data
    if os.path.getsize(results_file) > 0:
        # Clean data
        clean_data(results_file, os.path.join(current_search_dir, 'search_results_cleaned.csv'), verbose=verbose)
    else:
        print(f"Warning: The results file {results_file} is empty. No data to clean.")

def analyze_data_only(client_name, verbose):
    search_date_str = datetime.now().strftime('%Y-%m-%d')
    current_search_dir = os.path.join('results', client_name, search_date_str)
    cleaned_results_file = os.path.join(current_search_dir, 'search_results_cleaned.csv')

    roles_dir = os.path.join('results', client_name, 'roles')
    if not os.path.exists(roles_dir):
        print(f"Roles directory does not exist: {roles_dir}")
        return

    if os.path.exists(cleaned_results_file):
        analyse_data(cleaned_results_file, os.path.join(current_search_dir, 'search_results_analysed.csv'), roles_dir)
    else:
        print(f"Cleaned results file does not exist: {cleaned_results_file}")

def clean_and_analyze_data(client_name, verbose):
    clean_data_only(client_name, verbose)
    analyze_data_only(client_name, verbose)

def main():
    parser = argparse.ArgumentParser(description="Signal Enricher")
    parser.add_argument('--fetch', action='store_true', help="Only fetch data")
    parser.add_argument('--clean', action='store_true', help="Only clean data")
    parser.add_argument('--analyze', action='store_true', help="Only analyze data")
    args = parser.parse_args()

    client_name, _ = get_client_and_date()
    if client_name is None:
        return

    # Read search queries from file
    roles_dir = os.path.join('results', client_name, 'roles')
    with open(os.path.join(roles_dir, 'search_query.json'), 'r') as f:
        search_queries = json.load(f)
    queries = search_queries['queries']
    exclude = search_queries['exclude']

    # Read configuration
    with open('config/search_config.json', 'r') as f:
        config = json.load(f)
    days = config['days']
    num_results = config['num_results']
    num_pages = config['num_pages']
    verbose = config.get('verbose', False)
    sites = config.get('sites', [])
    search_date = config.get('search_date', datetime.now().strftime('%Y-%m-%d'))

    data_fetched = False
    if args.fetch or not (args.clean or args.analyze):
        data_fetched = fetch_data(client_name, days, num_results, num_pages, queries, exclude, sites, verbose)
    
    if (args.clean or not (args.fetch or args.analyze)) and (data_fetched or os.path.exists(os.path.join('results', client_name, search_date, 'search_results.csv'))):
        clean_data_only(client_name, verbose)
    elif not data_fetched:
        print("Skipping cleaning step as no data was fetched.")
    
    if (args.analyze or not (args.fetch or args.clean)) and (data_fetched or os.path.exists(os.path.join('results', client_name, search_date, 'search_results_cleaned.csv'))):
        analyze_data_only(client_name, verbose)
    elif not data_fetched:
        print("Skipping analysis step as no data was fetched.")

    print("Program finished successfully.")

if __name__ == "__main__":
    main()

```

### conftest.py

Описание: # conftest.py

```
# conftest.py

import sys
import os

# Добавляем корневую папку проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))
```



```

### results/example_task/roles/prompt.txt

Описание: Assignment for analyzing the text of articles:You will be analyzing text from an Excel spreadsheet consisting of news articles. The goal is to find specific companies that are planning a move, opening new offices (including coworking spaces), rebranding, mergers or acquisitions. The main goal is to find news that will allow the sales manager to make a more targeted offer for our product: assistance in the design and decoration of new offices.Criteria for correct analysis:- Suitable signals:- The name of the company is mentioned.- It is clear from the context that the company is opening new offices or developing co-working spaces.- The context indicates potential changes in the company's corporate image, plans for expansion or investment in infrastructure, which may include the need for office design services.- Discussion of corporate strategies for growth, rebranding, mergers and acquisitions, which may indicate a company's interest in updating its workspace or opening new offices.Unsuitable:- News about companies where new offices have already been opened and decorated.- Articles without mentioning a specific company or focused on market analyzes and statistics without specific examples of companies.- Information on market trends without specific examples of companies planning changes in the workspace.- General tips and strategies for companies on expansion, relocation, etc.- Advertising articles of competitors.Answer format:If you have found a suitable signal, please indicate the Name of the Company/Representative. If there is no suitable signal, the answer will be "0". The response must strictly contain either the company name with a representative (if specified) or "0", and be transmitted without any additional characters, text or quotation marks.

```
Assignment for analyzing the text of articles:You will be analyzing text from an Excel spreadsheet consisting of news articles. The goal is to find specific companies that are planning a move, opening new offices (including coworking spaces), rebranding, mergers or acquisitions. The main goal is to find news that will allow the sales manager to make a more targeted offer for our product: assistance in the design and decoration of new offices.Criteria for correct analysis:- Suitable signals:- The name of the company is mentioned.- It is clear from the context that the company is opening new offices or developing co-working spaces.- The context indicates potential changes in the company's corporate image, plans for expansion or investment in infrastructure, which may include the need for office design services.- Discussion of corporate strategies for growth, rebranding, mergers and acquisitions, which may indicate a company's interest in updating its workspace or opening new offices.Unsuitable:- News about companies where new offices have already been opened and decorated.- Articles without mentioning a specific company or focused on market analyzes and statistics without specific examples of companies.- Information on market trends without specific examples of companies planning changes in the workspace.- General tips and strategies for companies on expansion, relocation, etc.- Advertising articles of competitors.Answer format:If you have found a suitable signal, please indicate the Name of the Company/Representative. If there is no suitable signal, the answer will be "0". The response must strictly contain either the company name with a representative (if specified) or "0", and be transmitted without any additional characters, text or quotation marks.
```

### results/example_task/roles/search_query.json


```
{
    "queries": [
      "plans to open new office",
      "plans to expand office",
      "planning new office location",
      "announced plans for new office",
      "plans to relocate headquarters",
      "planning office expansion",
      "considering new office space",
      "plans to move office",
      "announced office relocation",
      "future office expansion plans",
      "intends to open new office",
      "planning to open new branch",
      "office expansion strategy",
      "announced new office plans",
      "plans to open new headquarters",
      "preparing to open new office",
      "planning office relocation",
      "new office space planning",
      "upcoming office expansion",
      "strategizing new office location"
    ],
    "exclude": "-\"opened a new office\" -\"recently opened\" -\"newly opened\" -\"has opened\" -\"just opened\" -\"office inauguration\" -\"officially opened\" -\"grand opening\" -\"new office opened\""
  }
```

### config/api_keys.py

Описание: api_keys = {

```
api_keys = {
    "xmlstock_user": "12230",
    "xmlstock_key": "c1dc3ea107e03a392e0d0432c6fe3348",
    "openai_api_key": "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",
    "gemeni_api_key": "AIzaSyATD9otC-y5T6uvYDfCODbaex1mLtJYdg0"
}

```

### config/__init__.py

Описание: Описание отсутствует

```

```

### config/search_config.json

Описание: {

```
{
  "days": 30,
  "num_results": 50,
  "num_pages": 1,
  "use_gemeni": true,
  "sites": [
      "https://www.linkedin.com/posts/"
  ]
}
```

### config/new_client_profile.json

Описание: {

```
{
    "client_name": "LC",
    "prompt": "You are analyzing text in an Excel spreadsheet consisting of news articles. Your task is to discover specific corporations interested in introducing innovations in the field of logistics. You need to find news that confirms these corporations' interest in the product: a base of startups that they can use to find and implement innovations and improve operational processes. Based on this news, the sales manager will be able to create a proposal for the product. For a correct analysis, consider the following criteria: Suitable signals: - The name of the corporation is mentioned. - It is clear from the context that the corporation is involved in logistics. - The context indicates the corporation's interest in innovating, using startups to improve its operational processes. Unsuitable: - Analytical reports, market reviews, etc. - News without mention of a specific corporation. - News about startups attracting investments from venture funds. Your answers will be recorded in a table and used as a filter. If you have found a suitable signal, determine the name of the client corporation and write only that. If there is no suitable signal, enter \"3\". The answer must be STRICTLY the company name or 3, without text, quotes or other characters.",
    "search_queries": {
      "queries": [
        "logistics tech startup collaboration",
        "supply chain innovation partnership",
        "shipping technology investment",
        "transportation startup accelerator",
        "3PL tech innovation",
        "trucking technology venture capital",
        "parcel delivery startup incubator",
        "cargo tech corporate venture",
        "fleet management technology pilot project",
        "emerging logistics solutions",
        "supply chain efficiency startup program",
        "freight technology R&D cooperation",
        "innovative shipping solutions investment",
        "smart transportation technologies",
        "3PL startup strategic investment",
        "next-gen trucking solutions",
        "cutting-edge parcel delivery startups",
        "cargo management technology",
        "fleet optimization startups",
        "logistics industry tech disruptors",
        "supply chain automation startups",
        "innovative freight processing technologies",
        "transportation safety tech ventures",
        "3PL sustainability innovations",
        "trucking logistics digital transformations",
        "parcel tracking tech startups",
        "cargo visibility solutions",
        "fleet management software innovations",
        "smart logistics platforms",
        "integrated supply chain systems"
      ],
      "exclude": "-vacancies -\"job postings\" -careers -hiring -workshops -seminars -training -\"trade shows\" -exhibitions -conferences -\"market analysis\" -\"financial reports\" -\"stock markets\" -legislation -regulations -compliance -courts -litigations"
    }
  }
```

### config/api_keys_example.py

Описание: api_keys = {

```
api_keys = {
    "xmlstock_user": "YOUR_XMLSTOCK_USER",
    "xmlstock_key": "YOUR_XMLSTOCK_KEY",
    "openai_api_key": "YOUR_OPENAI_API_KEY"
}
```

### modules/fetch_data.py

Описание: import requests

```
import requests
import pandas as pd
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from newspaper import Article
from config.api_keys import api_keys
from modules.date_utils import parse_date

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
        if verbose:
            print(f"Error fetching article: {url}\n{e}")
        return {
            'title': "N/A",
            'authors': [],
            'text': "",
            'article_url': url
        }
    except Exception as e:
        if verbose:
            print(f"Error parsing article: {url}\n{e}")
        return {
            'title': "N/A",
            'authors': [],
            'text': "",
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
```

### modules/clean_data.py

Описание: import pandas as pd

```
import pandas as pd
from fuzzywuzzy import fuzz

def clean_data(input_filename, output_filename, similarity_threshold=70, verbose=False):
    """
    Clean data by removing strict and non-strict duplicates.

    Args:
        input_filename (str): Path to the input CSV file.
        output_filename (str): Path to the output CSV file.
        similarity_threshold (int): Similarity threshold for fuzzy matching (default is 70).
        verbose (bool): Flag to enable/disable verbose output.

    Returns:
        None
    """
    if verbose:
        print(f"Loading data from file {input_filename}...")
    df = pd.read_csv(input_filename)

    # Stage 1: "Strict" comparison and removal of exact duplicates
    if verbose:
        print("Removing strict duplicates...")
    df_no_strict_duplicates = df.drop_duplicates(subset=['title', 'description']).reset_index(drop=True)
    if verbose:
        print(f"Strict duplicates removed: {len(df) - len(df_no_strict_duplicates)}")

    # Stage 2: Preparation for "non-strict" comparison
    if verbose:
        print("Preparing data for 'non-strict' comparison...")
    df_no_strict_duplicates_sorted = df_no_strict_duplicates.sort_values('title').reset_index()

    # List of row indices to remove
    indexes_to_remove = set()

    if verbose:
        print("Searching for duplicates with 'non-strict' comparison...")
    # Use fuzzy matching algorithm to find duplicates
    for i in range(len(df_no_strict_duplicates_sorted) - 1):
        for j in range(i + 1, len(df_no_strict_duplicates_sorted)):
            # Use fuzz.token_sort_ratio to compare strings
            similarity_title = fuzz.token_sort_ratio(df_no_strict_duplicates_sorted.loc[i, 'title'], df_no_strict_duplicates_sorted.loc[j, 'title'])
            similarity_text = fuzz.token_sort_ratio(df_no_strict_duplicates_sorted.loc[i, 'description'], df_no_strict_duplicates_sorted.loc[j, 'description'])

            if similarity_title > similarity_threshold or similarity_text > similarity_threshold:
                indexes_to_remove.add(df_no_strict_duplicates_sorted.loc[j, 'index'])  # Add index to set for removal
                if verbose:
                    print(f"Duplicate found: row {i + 1} and row {j + 1}")
                    print(f"Title similarity: {similarity_title}, Text similarity: {similarity_text}")

    # Remove duplicates found in the 'non-strict' comparison stage
    df_final = df_no_strict_duplicates_sorted.drop(df_no_strict_duplicates_sorted[df_no_strict_duplicates_sorted['index'].isin(indexes_to_remove)].index).reset_index(drop=True)

    if verbose:
        print("Saving data...")
    # Save cleaned data back to CSV
    df_final.to_csv(output_filename, index=False)

    # Output information about the number of removed and remaining rows
    if verbose:
        print(f"Rows removed in 'non-strict' comparison stage: {len(indexes_to_remove)}")
        print(f"Remaining rows after cleaning: {len(df_final)}")
        print(f"Data cleaned and saved to '{output_filename}'.")

if __name__ == "__main__":
    # Example usage
    input_filename = 'results/example_client/2024-06-13/search_results.csv'
    output_filename = 'results/example_client/2024-06-13/search_results_cleaned.csv'
    clean_data(input_filename, output_filename, verbose=True)
```

### modules/utils.py

Описание: import os

```
import os
import sys
import signal
import openai
import google.generativeai as genai
from config.api_keys import api_keys
import json

# Set the OpenAI API key
openai.api_key = api_keys["openai_api_key"]

# Load the configuration
with open('config/search_config.json', 'r') as f:
    config = json.load(f)

use_gemeni = config.get("use_gemeni", False)
gemeni_api_key = api_keys["gemeni_api_key"]

# Configure Gemini API
if use_gemeni:
    genai.configure(api_key=gemeni_api_key)

def load_role_description(file_path):
    """
    Load the role description from a file.

    Args:
        file_path (str): Path to the file containing the role description.

    Returns:
        str: The role description text.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def signal_handler(sig, frame, workbook, filename, verbose=False):
    """
    Signal handler for saving and closing the workbook on interrupt.

    Args:
        sig (int): Signal number.
        frame (frame): Current stack frame.
        workbook (Workbook): Workbook object to save and close.
        filename (str): Path to the file to save the workbook.
        verbose (bool): Flag to enable/disable verbose output.
    """
    if verbose:
        print('You pressed Control+C! Saving and closing the file...')
    workbook.save(filename)
    workbook.close()
    sys.exit(0)

def gpt_query(messages):
    """
    Query the GPT-4 model or Gemeni model based on configuration.

    Args:
        messages (list): List of messages to send to the model.

    Returns:
        tuple: A tuple containing the response content and the number of tokens used.
    """
    if use_gemeni:
        # Gemeni API request
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare the prompt
        prompt = f"System: {messages[0]['content']}\nHuman: Analyze the following article:\n\n{messages[1]['content']}"
        
        response = model.generate_content(prompt)
        content = response.text
        tokens_used = len(prompt.split()) + len(content.split())  # Простая оценка количества токенов
        return content, tokens_used
    else:
        # OpenAI GPT-4 API request
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=100,
            temperature=0.3
        )
        content = response.choices[0].message['content']
        tokens_used = response['usage']['total_tokens']
        return content, tokens_used
```

### modules/analyse_data.py

Описание: # modules/analyse_data.py

```
# modules/analyse_data.py

import os
import pandas as pd
from openpyxl import load_workbook
from modules.utils import load_role_description, signal_handler, gpt_query

def analyse_data(input_filename, output_filename, roles_dir):
    # Путь к файлу с ролями
    role_file = os.path.join(roles_dir, 'prompt.txt')

    # Загрузка описания роли
    role_description = load_role_description(role_file)

    # Загрузка данных из CSV
    print(f"Loading data from {input_filename}...")
    df = pd.read_csv(input_filename)
    print(f"Loaded {len(df)} rows.")

    # Добавление колонки для результатов анализа
    df['analysis'] = ""

    # Счетчик использованных токенов
    tokens_used_total = 0

    # Анализ данных
    for index, row in df.iterrows():
        full_article_text = row['description'] or ""
        try:
            if len(full_article_text) >= 100:
                # Обрезаем текст, если он слишком длинный
                if len(full_article_text) > 2000:
                    full_article_text = full_article_text[:2000]

                # Анализ полного текста статьи
                article_messages = [
                    {"role": "system", "content": role_description},
                    {"role": "user", "content": full_article_text}
                ]
                print(f"Querying model for row {index + 1}...")
                answer_article, tokens_used_article = gpt_query(article_messages)
                tokens_used_total += tokens_used_article

                # Вывод результатов анализа и использованных токенов
                print(f"Row {index + 1}:")
                print(f" Analysis response: {answer_article[:100]}...")  # Print first 100 characters
                print(f" Tokens used for article: {tokens_used_article}")

                # Запись результата в DataFrame
                df.at[index, 'analysis'] = answer_article
            else:
                print(f"Row {index + 1}: article text too short for analysis. Length: {len(full_article_text)}")
        except Exception as e:
            print(f"Error processing row {index + 1}: {e}")
        
        # Save results after each processed row
        df.to_csv(output_filename, index=False)
        print(f"Results saved to '{output_filename}'. Processed {index + 1} rows.")

    print(f"Processing completed. Total tokens used: {tokens_used_total}")
    print(f"Final results saved to '{output_filename}'.")
```

### modules/__init__.py

Описание: Описание отсутствует

```

