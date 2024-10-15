import os
import pandas as pd
import asyncio
import argparse
import time
import re
from datetime import datetime
from modules.client_management import get_client_and_date
from modules.utils import load_role_description, gpt_query_async, clean_text, truncate_text

class RateLimiter:
    def __init__(self, max_rate, period=60):
        self.max_rate = max_rate
        self.period = period
        self.tokens = max_rate
        self.updated_at = time.monotonic()

    async def acquire(self):
        while True:
            now = time.monotonic()
            time_passed = now - self.updated_at
            self.tokens += time_passed * (self.max_rate / self.period)
            if self.tokens > self.max_rate:
                self.tokens = self.max_rate
            self.updated_at = now

            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            sleep_time = (1 - self.tokens) / (self.max_rate / self.period)
            await asyncio.sleep(sleep_time)

async def analyze_apolo_data(input_file, output_file, role_file, start_row=0, rate_limit=20):
    print(f"Начинаем анализ данных из файла: {input_file}")
    
    # Загрузка описания роли
    role_description = load_role_description(role_file)
    
    # Загрузка данных из CSV
    df = pd.read_csv(input_file)
    print(f"Загружено {len(df)} строк.")
    
    # Добавление новых колонок для результатов анализа
    for col in ['Analysis_1', 'Analysis_2', 'Analysis_3', 'Raw_Response']:
        if col not in df.columns:
            df[col] = ''
    
    # Создание ограничителя скорости
    rate_limiter = RateLimiter(max_rate=rate_limit)
    
    async def process_row(index, row):
        if index < start_row:
            return
        
        try:
            # Подготовка данных для анализа
            website = clean_text(row['Website'])
            linkedin_url = clean_text(row['Company Linkedin Url'])
            description = clean_text(row['Short Description'])
            
            # Формирование запроса для модели
            query = f"""Website: {website}
LinkedIn: {linkedin_url}
Description: {description}

Please analyze this company based on the provided information and answer the following questions:
1. Does this company fit the description in your instructions? (Yes/No)
2. What is the sales signal strength for this company? (None/Weak/Moderate/Strong)
3. Provide a brief note explaining your analysis and decision.

Return your answer as a Python list with 3 elements: [answer1, answer2, answer3]"""
            
            # Ожидание разрешения от ограничителя скорости
            await rate_limiter.acquire()
            
            # Отправка запроса к LLM
            response, _ = await gpt_query_async([
                {"role": "system", "content": role_description},
                {"role": "user", "content": query}
            ])
            
            print(f"\nСырой ответ модели для строки {index + 1}:\n{response}\n")
            
            # Разбор ответа модели
            analysis_1, analysis_2, analysis_3 = parse_llm_response(response)
            
            # Запись результатов в DataFrame
            df.at[index, 'Analysis_1'] = analysis_1
            df.at[index, 'Analysis_2'] = analysis_2
            df.at[index, 'Analysis_3'] = analysis_3
            df.at[index, 'Raw_Response'] = response
            
            print(f"Обработана строка {index + 1}: {row['Company Name for Emails']}")
            print(f"Analysis_1: {analysis_1}")
            print(f"Analysis_2: {analysis_2}")
            print(f"Analysis_3: {analysis_3}")
            
            # Сохранение результатов каждые 30 строк
            if (index + 1) % 30 == 0:
                df.to_excel(output_file, index=False)
                print(f"Промежуточные результаты сохранены в {output_file}")
        
        except Exception as e:
            print(f"Ошибка при обработке строки {index + 1}: {str(e)}")
    
    # Обработка всех строк
    tasks = [process_row(index, row) for index, row in df.iterrows()]
    await asyncio.gather(*tasks)
    
    # Финальное сохранение результатов
    df.to_excel(output_file, index=False)
    print(f"Анализ завершен. Результаты сохранены в {output_file}")

def parse_llm_response(response):
    # Удаляем лишние пробелы и переносы строк
    response = response.strip()
    
    # Попытка извлечь содержимое квадратных скобок
    match = re.search(r'\[(.*?)\]', response, re.DOTALL)
    if match:
        content = match.group(1)
    else:
        content = response
    
    # Разделение на части по запятым, но не внутри кавычек
    parts = re.split(r',\s*(?=[^"]*(?:"[^"]*"[^"]*)*$)', content)
    
    # Очистка частей от кавычек и лишних пробелов
    parts = [part.strip().strip('"') for part in parts]
    
    # Возвращаем три части (или меньше, если частей меньше трех)
    return parts[:3] if len(parts) >= 3 else parts + [''] * (3 - len(parts))

async def main():
    parser = argparse.ArgumentParser(description="Apolo Data Analyzer")
    parser.add_argument('--continue_from', type=int, help="Continue analysis from specified row number")
    args = parser.parse_args()

    client_name, search_date = get_client_and_date()
    if client_name is None:
        return

    search_date_str = search_date.strftime('%Y-%m-%d')
    input_dir = os.path.join('results', client_name, search_date_str)
    
    # Поиск CSV файла в директории
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    if not csv_files:
        print(f"CSV файл не найден в директории {input_dir}")
        return
    
    input_file = os.path.join(input_dir, csv_files[0])
    output_file = os.path.join(input_dir, f"{os.path.splitext(csv_files[0])[0]}_analyzed.xlsx")
    role_file = os.path.join('results', client_name, 'roles', 'prompt.txt')

    start_row = 0
    if args.continue_from:
        start_row = args.continue_from
        print(f"Продолжение анализа с строки {start_row}")

    await analyze_apolo_data(input_file, output_file, role_file, start_row)

if __name__ == "__main__":
    asyncio.run(main())