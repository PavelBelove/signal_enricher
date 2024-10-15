"""
Этот скрипт преобразует данные о компаниях из текстового файла в таблицу Excel.

Инструкция по использованию:
1. Убедитесь, что у вас установлен Python 3.x (https://www.python.org/downloads/)
2. Установите необходимые библиотеки. Откройте командную строку и выполните:
   pip install pandas openpyxl

3. Подготовьте входной текстовый файл:
   - Каждая компания должна быть отделена одной или несколькими пустыми строками
   - Информация о каждой компании должна быть представлена в виде списка характеристик

4. Сохраните этот скрипт в файл с расширением .py (например, company_data_to_excel.py)

5. В скрипте укажите:
   - Путь к входному файлу (переменная input_file)
   - Желаемое имя выходного Excel-файла (переменная output_file)

6. Запустите скрипт:
   - Откройте командную строку
   - Перейдите в папку со скриптом: cd путь/к/папке/со/скриптом
   - Выполните команду: python company_data_to_excel.py

7. После выполнения скрипта, вы увидите сообщение об успешном создании Excel-файла

Примечание: Если вам нужно изменить список или порядок столбцов в итоговой таблице, 
отредактируйте список 'columns' в функции create_excel().
"""

import pandas as pd
import re

def parse_company_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    companies = re.split(r'\n\s*\n', content.strip())
    
    data = []
    for company in companies:
        company_data = company.split('\n')
        row = {}
        for field in company_data:
            if ' - ' in field:
                continue  # Пропускаем строки с логотипами
            if ':' in field:
                key, value = field.split(':', 1)
                row[key.strip()] = value.strip()
            else:
                row[len(row)] = field.strip()
        data.append(row)

    return data

def create_excel(data, output_file):
    columns = [
        'Transaction name',
        'Organization name',
        'Founding type',
        'Investment size',
        'Investment date',
        'Founding stage',
        'Organization description',
        'Industry',
        'Website',
        'Organization location',
        'Total funding amount',
        'Founding status',
        'Number of founders',
        'Investor names',
        'Lead investors',
        'Number of investors'
    ]

    df = pd.DataFrame(data)
    
    # Переименовываем столбцы в соответствии с желаемым порядком
    df = df.rename(columns={
        0: 'Transaction name',
        1: 'Organization name',
        2: 'Founding type',
        3: 'Investment size',
        4: 'Investment date',
        5: 'Founding stage',
        6: 'Organization description',
        7: 'Industry',
        8: 'Website',
        9: 'Organization location',
        10: 'Total funding amount',
        11: 'Founding status',
        12: 'Number of founders',
        13: 'Investor names',
        14: 'Lead investors',
        15: 'Number of investors'
    })
    
    # Выбираем только нужные столбцы и в нужном порядке
    df = df[columns]

    # Сохраняем в Excel
    df.to_excel(output_file, index=False, engine='openpyxl')

if __name__ == "__main__":
    input_file = "scripts/companies.txt"  # Укажите путь к вашему входному файлу
    output_file = "scripts/companies_data.xlsx"  # Укажите желаемое имя для выходного файла Excel

    data = parse_company_data(input_file)
    create_excel(data, output_file)
    print(f"Данные успешно сохранены в файл {output_file}")