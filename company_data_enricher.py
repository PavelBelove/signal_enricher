# Файл: ./company_data_enricher.py

import os
import argparse
from datetime import datetime
from modules.fetch_company_data import run_fetch_company_data
from modules.analyse_data import run_analyse_data
from modules.client_management import get_client_and_date
from modules.utils import load_config
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Обогащение данных компаний")
    parser.add_argument('--fetch', action='store_true', help="Только получение данных")
    parser.add_argument('--analyze', action='store_true', help="Только анализ данных")
    args = parser.parse_args()

    try:
        client_name, search_date = get_client_and_date()
        if client_name is None:
            return

        print(f"Клиент: {client_name}, Дата: {search_date}")

        search_date_str = search_date.strftime('%Y-%m-%d')

        config = load_config(os.path.join('results', client_name, 'roles', 'config.json'))
        
        input_file = os.path.join('results', client_name, search_date_str, config['input_file'])
        if not os.path.exists(input_file):
            print(f"Входной файл {input_file} не найден.")
            return

        if args.fetch or not args.analyze:
            print("Начинаем получение данных...")
            output_file = os.path.join('results', client_name, search_date_str, 'fetched_company_data.csv')
            run_fetch_company_data(input_file, output_file, config)
            if not os.path.exists(output_file):
                print(f"Ошибка: Файл {output_file} не был создан.")
                return
            print(f"Данные получены и сохранены в {output_file}")
        
        if args.analyze or not args.fetch:
            print("Начинаем анализ данных...")
            input_file = os.path.join('results', client_name, search_date_str, 'fetched_company_data.csv')
            if not os.path.exists(input_file):
                print(f"Ошибка: Файл {input_file} не существует.")
                return
            output_file = os.path.join('results', client_name, search_date_str, 'analyzed_data.csv')
            
            run_analyse_data(input_file, output_file, os.path.join('results', client_name, 'roles'))
            print(f"Данные проанализированы и сохранены в {output_file}")

        print("Программа успешно завершена.")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()