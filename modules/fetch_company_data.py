# Файл: ./modules/fetch_company_data.py

import pandas as pd
import asyncio
import csv
import os
from modules.fetch_data import fetch_xmlstock_search_results, process_search_results
from modules.utils import clean_domain

async def fetch_company_data(input_file, output_file, config):
    """
    Получает данные о компаниях из входного Excel файла, проводит поиск и сохраняет результаты в новый CSV файл.
    """
    try:
        # Пробуем разные способы чтения файла
        try:
            df = pd.read_excel(input_file, engine='openpyxl')
        except:
            try:
                df = pd.read_csv(input_file, encoding='utf-8')
            except:
                df = pd.read_csv(input_file, encoding='latin1')
        
        print(f"Успешно загружено {len(df)} строк из входного файла.")
        print(f"Колонки: {df.columns.tolist()}")
    except Exception as e:
        print(f"Ошибка при чтении входного файла: {str(e)}")
        return

    results = []

    # Получение параметров из конфигурации
    search_column = config['search_column']
    search_queries = config['search_queries']
    use_domain = config.get('use_domain', False)
    company_name_column = config['company_name_column']

    # Проверка наличия необходимых колонок
    required_columns = [company_name_column, search_column, 'Organization description']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"В входном файле отсутствуют следующие колонки: {', '.join(missing_columns)}")

    # Функция для сохранения промежуточных результатов
    def save_results(results, output_file, mode='w'):
        df_results = pd.DataFrame(results)
        if 'Organization description' in df_results.columns:
            df_results = df_results.rename(columns={'Organization description': 'description'})
        df_results.to_csv(output_file, mode=mode, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
        print(f"Результаты сохранены в {output_file}")

    companies_processed = 0

    for index, row in df.iterrows():
        company_name = row[company_name_column]
        search_value = row[search_column]

        # Проверка на NaN значения
        if pd.isna(search_value):
            print(f"Пропуск компании {company_name}: отсутствует значение для поиска")
            continue

        # Очистка домена, если используется поиск по сайту
        if use_domain:
            search_value = clean_domain(str(search_value))
            search_prefix = f"site:{search_value}"
        else:
            search_prefix = str(search_value)

        company_results = []

        # Выполнение поиска для каждого запроса
        for query in search_queries:
            full_query = f"{search_prefix} {query}"
            print(f"Поиск для компании {company_name}: {full_query}")

            # Получение результатов поиска
            search_results = await fetch_xmlstock_search_results(full_query, "", "", config)
            if search_results:
                # Обработка найденных статей
                articles = await process_search_results(search_results)
                for article in articles:
                    result = row.to_dict()  # Копируем все данные из исходной строки
                    result.update({
                        'company_name': company_name,
                        'search_query': full_query,
                        'title': article['title'],
                        'link': article['article_url'],
                        'found_text': article['text'][:1000],  # Берем первые 1000 символов текста
                        'description': article['text']  # Сохраняем полный текст статьи
                    })
                    company_results.append(result)
                    
                    print(f"\nРезультаты парсинга для {company_name}:")
                    print(f"Заголовок: {article['title']}")
                    print(f"Ссылка: {article['article_url']}")
                    print(f"Первые 1000 символов текста: {article['text'][:1000]}")
                    print("-" * 50)
                    
                    break  # Берем только первый результат для каждого запроса

            # Задержка между запросами
            await asyncio.sleep(config.get('delay_between_queries', 1))

        # Если найдены результаты для компании, добавляем их в общий список
        if company_results:
            results.extend(company_results)
        else:
            # Если результатов нет, добавляем строку с пустым found_text
            result = row.to_dict()
            result.update({
                'company_name': company_name,
                'search_query': '',
                'title': '',
                'link': '',
                'found_text': '',
                'description': ''
            })
            results.append(result)

        companies_processed += 1

        # Сохранение промежуточных результатов каждые 10 обработанных компаний
        if companies_processed % 10 == 0:
            save_results(results, output_file, mode='a' if companies_processed > 10 else 'w')
            results = []  # Очищаем список результатов после сохранения

    # Сохранение оставшихся результатов
    if results:
        save_results(results, output_file, mode='a' if companies_processed > 10 else 'w')

    print(f"Обработка завершена. Всего обработано компаний: {companies_processed}")

# Функция-обертка для запуска асинхронной функции
def run_fetch_company_data(input_file, output_file, config):
    asyncio.run(fetch_company_data(input_file, output_file, config))