import os
import json
import argparse
from datetime import datetime
from modules.fetch_data import fetch_xmlstock_search_results, fetch_and_parse #, save_results_to_csv
from modules.clean_data import clean_data
from modules.analyse_data import analyse_data
from modules.client_management import get_client_and_date
from modules.utils import save_results_to_csv

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
            print(f"Processing article: {result['link']}")
            article_data = fetch_and_parse(result['link'])
            print(f"Article title: {article_data['title']}")
            print(f"Article text length: {len(article_data['text'])}")
            if article_data['title'] != "": #"N/A":
                result.update({
                    'description': article_data['text'],
                    'query': query
                })
                all_articles.append(result)
            else:
                print(f"Article skipped: {result['link']}")
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
