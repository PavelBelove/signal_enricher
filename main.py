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

def fetch_data(client_name, days, num_results, num_pages, queries, exclude, verbose):
    print("Starting data fetching and processing...")
    # Fetch and process data
    all_articles = []
    for query in queries:
        search_results = fetch_xmlstock_search_results(query, days, num_results, num_pages)
        for result in search_results:
            article_data = fetch_and_parse(result['link'])
            if article_data['title'] != "N/A":
                result.update({
                    'description': article_data['text'],
                    'query': query
                })
                all_articles.append(result)
        time.sleep(2)  # Add delay between requests

    # Save results to CSV
    search_date_str = datetime.now().strftime('%Y-%m-%d')
    current_search_dir = os.path.join('results', client_name, search_date_str)
    os.makedirs(current_search_dir, exist_ok=True)
    results_file = os.path.join(current_search_dir, 'search_results.csv')
    save_results_to_csv(all_articles, results_file)

def clean_data_only(client_name, verbose):
    search_date_str = datetime.now().strftime('%Y-%m-%d')
    current_search_dir = os.path.join('results', client_name, search_date_str)
    results_file = os.path.join(current_search_dir, 'search_results.csv')

    # Check if the results file is empty before calling clean_data
    if os.path.getsize(results_file) > 0:
        # Clean data
        clean_data(results_file, os.path.join(current_search_dir, 'search_results_cleaned.csv'), verbose=verbose)
    else:
        print("No articles were extracted. Skipping data cleaning.")

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
    search_date = config.get('search_date', datetime.now().strftime('%Y-%m-%d'))

    if args.fetch:
        fetch_data(client_name, days, num_results, num_pages, queries, exclude, verbose)
    elif args.clean:
        clean_data_only(client_name, verbose)
    elif args.analyze:
        analyze_data_only(client_name, verbose)
    else:
        fetch_data(client_name, days, num_results, num_pages, queries, exclude, verbose)
        clean_and_analyze_data(client_name, verbose)

    print("Program finished successfully.")

if __name__ == "__main__":
    main()
    