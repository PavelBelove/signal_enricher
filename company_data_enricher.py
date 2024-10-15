# Файл: ./company_data_enricher.py

import os
import argparse
from datetime import datetime
from modules.fetch_company_data import run_fetch_company_data
from modules.analyse_data import run_analyse_data
from modules.client_management import get_client_and_date
from modules.utils import load_config
import pandas as pd
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def remove_duplicate_headers(file_path):
    """
    Удаляет дублирующиеся заголовки из CSV-файла.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        return
    header = lines[0]
    data_lines = [header] + [line for line in lines[1:] if line.strip() and not line.startswith(header)]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(data_lines)
    logging.info(f"Удалены повторяющиеся заголовки из {file_path}")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Обогащение данных компаний")
    parser.add_argument('--fetch', action='store_true', help="Только получение данных")
    parser.add_argument('--analyze', action='store_true', help="Только анализ данных")
    args = parser.parse_args()

    try:
        client_name, search_date = get_client_and_date()
        if client_name is None:
            logging.error("Клиент не найден. Завершение программы.")
            return

        logging.info(f"Клиент: {client_name}, Дата: {search_date}")

        search_date_str = search_date.strftime('%Y-%m-%d')

        config_path = os.path.join('results', client_name, 'roles', 'config.json')
        if not os.path.exists(config_path):
            logging.error(f"Конфигурационный файл {config_path} не найден.")
            return

        config = load_config(config_path)

        input_file = os.path.join('results', client_name, search_date_str, config['input_file'])
        if not os.path.exists(input_file):
            logging.error(f"Входной файл {input_file} не найден.")
            return

        fetched_file = os.path.join('results', client_name, search_date_str, 'fetched_company_data.csv')
        analyzed_file = os.path.join('results', client_name, search_date_str, 'analyzed_data.csv')

        if args.fetch or not args.analyze:
            logging.info("Начинаем получение данных...")
            run_fetch_company_data(input_file, fetched_file, config)
            if not os.path.exists(fetched_file):
                logging.error(f"Ошибка: Файл {fetched_file} не был создан.")
                return
            # Удаляем вызов remove_duplicate_headers
            # remove_duplicate_headers(fetched_file)
            logging.info(f"Данные получены и сохранены в {fetched_file}")

        if args.analyze or not args.fetch:
            logging.info("Начинаем анализ данных...")
            if not os.path.exists(fetched_file):
                logging.error(f"Ошибка: Файл {fetched_file} не существует.")
                return

            # Удаляем вызов remove_duplicate_headers
            # remove_duplicate_headers(fetched_file)

            # Передача всей конфигурации для обеспечения выбора модели в модуле анализа
            logging.info(f"Используемая конфигурация для запроса: {config}")

            run_analyse_data(fetched_file, analyzed_file, os.path.join('results', client_name, 'roles'), config)
            if not os.path.exists(analyzed_file):
                logging.error(f"Ошибка: Файл {analyzed_file} не был создан.")
                return
            # Удаляем вызов remove_duplicate_headers
            # remove_duplicate_headers(analyzed_file)
            logging.info(f"Данные проанализированы и сохранены в {analyzed_file}")

        logging.info("Программа успешно завершена.")

    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
