import os
import json
import argparse
from datetime import datetime
from modules.fetch_data import fetch_xmlstock_search_results, fetch_and_parse, save_results_to_csv
from modules.clean_data import clean_data
from modules.analyse_data import analyse_data
from modules.client_management import get_client_and_date
from modules.proxy_manager import ProxyManager

import time
import pandas as pd

def get_proxy_dict(proxy):
    return {'http': proxy, 'https': proxy}

def fetch_data(client_name, days, num_results, num_pages, queries, exclude, sites, verbose):
    print("Начинаем получение и обработку данных...")
    all_articles = []
    for query in queries:
        print(f"Получаем данные для запроса: {query}")
        search_results = fetch_xmlstock_search_results(query, days, num_results, num_pages, sites, verbose)
        print(f"Получено {len(search_results)} результатов для запроса: {query}")
        for result in search_results:
            print(f"Обрабатываем статью: {result['link']}")
            article_data = fetch_and_parse(result['link'], verbose)
            print(f"Заголовок статьи: {article_data['title']}")
            print(f"Длина текста статьи: {len(article_data['text'])}")
            if article_data['title'] != "":
                result.update({
                    'description': article_data['text'],
                    'query': query
                })
                all_articles.append(result)
            else:
                print(f"Статья пропущена: {result['link']}")
        time.sleep(2)

    print(f"Всего получено статей: {len(all_articles)}")

    search_date_str = datetime.now().strftime('%Y-%m-%d')
    current_search_dir = os.path.join('results', client_name, search_date_str)
    os.makedirs(current_search_dir, exist_ok=True)
    results_file = os.path.join(current_search_dir, 'search_results.csv')
    
    if len(all_articles) > 0:
        save_results_to_csv(all_articles, results_file, verbose)
        print(f"Результаты сохранены в {results_file}")
    else:
        print("Статьи не были получены. Файл результатов не был создан.")

    return len(all_articles) > 0

def main():
    parser = argparse.ArgumentParser(description="Signal Enricher")
    parser.add_argument('--fetch', action='store_true', help="Только получение данных")
    parser.add_argument('--clean', action='store_true', help="Только очистка данных")
    parser.add_argument('--analyze', action='store_true', help="Только анализ данных")
    args = parser.parse_args()

    try:
        client_name, search_date = get_client_and_date()
        if client_name is None:
            return

        print(f"Клиент: {client_name}, Дата: {search_date}")

        search_date_str = search_date.strftime('%Y-%m-%d')

        file_path = os.path.join('results', client_name, search_date_str, 'search_results.csv')
        print(f"Ищем файл: {file_path}")
        if os.path.exists(file_path):
            print("Файл найден")
            print(f"Размер файла: {os.path.getsize(file_path)} байт")
        else:
            print("Файл не найден")

        roles_dir = os.path.join('results', client_name, 'roles')
        with open(os.path.join(roles_dir, 'search_query.json'), 'r') as f:
            search_queries = json.load(f)
        queries = search_queries['queries']
        exclude = search_queries['exclude']

        with open('config/search_config.json', 'r') as f:
            config = json.load(f)
        days = config['days']
        num_results = config['num_results']
        num_pages = config['num_pages']
        verbose = config.get('verbose', False)
        sites = config.get('sites', [])

        data_fetched = False
        if args.fetch or not (args.clean or args.analyze):
            data_fetched = fetch_data(client_name, days, num_results, num_pages, queries, exclude, sites, verbose)
        
        if (args.clean or not (args.fetch or args.analyze)) and (data_fetched or os.path.exists(file_path)):
            print("Начинаем очистку данных...")
            output_file = os.path.join('results', client_name, search_date_str, 'search_results_cleaned.csv')
            print(f"Входной файл: {file_path}")
            print(f"Выходной файл: {output_file}")
            
            if os.path.getsize(file_path) > 0:
                print("Вызываем функцию clean_data()...")
                try:
                    print("Перед вызовом clean_data()")
                    rows_before, rows_after = clean_data(file_path, output_file, verbose=True)  # Всегда используем verbose=True для отладки
                    print("После вызова clean_data()")
                    print(f"Очистка данных завершена. Было строк: {rows_before}, стало строк: {rows_after}")
                    print(f"Удалено дубликатов: {rows_before - rows_after}")
                except Exception as e:
                    print(f"Ошибка при очистке данных: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"Предупреждение: Входной файл {file_path} пуст. Очистка данных не выполнена.")
        elif not data_fetched:
            print("Пропускаем этап очистки, так как данные не были получены.")
        
        cleaned_file = os.path.join('results', client_name, search_date_str, 'search_results_cleaned.csv')
        if (args.analyze or not (args.fetch or args.clean)) and (data_fetched or os.path.exists(cleaned_file)):
            analyse_data(cleaned_file, 
                         os.path.join('results', client_name, search_date_str, 'search_results_analysed.csv'), 
                         os.path.join('results', client_name, 'roles'))
        elif not data_fetched:
            print("Пропускаем этап анализа, так как данные не были получены.")

        print("Программа успешно завершена.")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    