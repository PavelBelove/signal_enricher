import pandas as pd
import json
import requests

# Загрузка файла Excel
excel_file_path = './scripts/companies_data.xlsx'

# Функция для получения текущего курса валют с открытого API
def get_exchange_rates():
    url = "https://api.exchangerate-api.com/v4/latest/EUR"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['rates']
    else:
        raise Exception("Не удалось получить курсы валют")

# Функция для конвертации валюты в евро с округлением до целого значения
def convert_to_euro(value, currency, rates):
    if currency == '€':
        return round(value) if value else 'N/A'  # Уже в евро, округляем до целого
    if currency == '$':
        return round(value / rates['USD']) if value else 'N/A'  # Конвертация из долларов в евро
    if currency == '£':
        return round(value / rates['GBP']) if value else 'N/A'  # Конвертация из фунтов в евро
    # Добавьте другие валюты по необходимости
    return 'N/A'  # Если неизвестная валюта или некорректное значение, возвращаем 'N/A'

# Основная функция обработки таблицы
def process_table(excel_path, config_path):
    # Чтение конфигурационного файла
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Загрузка таблицы
    df = pd.read_excel(excel_path)

    # Фильтрация по ключевым словам
    industry_keywords = config['Industry']
    location_keywords = config['Location']

    # Фильтруем строки по Industry
    df_filtered = df[df['Industry'].str.contains('|'.join(industry_keywords), case=False, na=False)]

    # Фильтруем строки по Organization location
    df_filtered = df_filtered[df_filtered['Organization location'].str.contains('|'.join(location_keywords), case=False, na=False)]

    # Получаем курсы валют
    exchange_rates = get_exchange_rates()

    # Добавляем колонку для конвертации валют
    def extract_currency_symbol(value):
        if isinstance(value, str):
            for symbol in ['€', '$', '£']:
                if symbol in value:
                    return symbol
        return None

    def extract_value(value):
        if isinstance(value, str):
            # Извлекаем числовую часть из строки, удаляем прочерки и пробелы
            clean_value = ''.join(filter(str.isdigit, value.replace('-', '').replace(' ', '')))
            if clean_value:  # Если что-то осталось после фильтрации
                try:
                    return float(clean_value)
                except ValueError:
                    return None  # Если не удалось преобразовать, возвращаем None
        elif isinstance(value, (int, float)):
            return value  # Если уже число, просто возвращаем
        return None  # Если значение некорректно, возвращаем None

    # Применяем функции к колонкам
    df_filtered['Currency'] = df_filtered['Investment size'].apply(extract_currency_symbol)
    df_filtered['Investment size'] = df_filtered['Investment size'].apply(extract_value)
    df_filtered['Amount in Euro'] = df_filtered.apply(
        lambda row: convert_to_euro(row['Investment size'], row['Currency'], exchange_rates), axis=1
    )

    # Заполняем пустые значения 'N/A' в колонке 'Amount in Euro'
    df_filtered['Amount in Euro'].fillna('N/A', inplace=True)

    # Сохраняем результат в новый файл
    output_file = './scripts/processed_companies_data.xlsx'
    df_filtered.to_excel(output_file, index=False)
    return output_file

# Путь к конфигурационному файлу
config_file_path = './scripts/config.json'

# Выполняем обработку
output_path = process_table(excel_file_path, config_file_path)

print(f"Таблица сохранена по пути: {output_path}")
