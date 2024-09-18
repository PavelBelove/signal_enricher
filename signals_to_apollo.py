import csv
import time
import re
import codecs
from urllib.parse import urlparse
import pandas as pd

def detect_encoding(file_path):
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1']
    for encoding in encodings:
        try:
            with codecs.open(file_path, 'r', encoding=encoding) as file:
                file.read()
            return encoding
        except UnicodeDecodeError:
            continue
    return None

def clean_url(url):
    if not url:
        return ''
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    domain = re.sub(r'^www\.', '', domain)
    return domain.lower().strip()

def print_debug_info(row_num, website, clean_row, matched, company_name=''):
    print(f"\nОтладка для строки {row_num}:")
    print(f"Website (после очистки): {website}")
    print(f"Company name: {company_name}")
    print(f"Matched: {matched}")
    if matched:
        print(f"Source: {clean_row['Source']}")
        print(f"Signal: {clean_row['Signal']}")
        print(f"Signal presence: {clean_row['Signal presence']}")

def process_pharma_data(excel_file, target_csv, output_csv):
    start_time = time.time()
    
    target_encoding = detect_encoding(target_csv)
    
    print(f"Кодировка целевого файла: {target_encoding}")
    
    # Read Excel file
    excel_data = pd.read_excel(excel_file)
    print(f"Всего строк в Excel файле: {len(excel_data)}")
    
    cleaned_data = {}
    skipped_rows = 0
    empty_source = 0
    duplicate_cleaned_urls = 0

    for index, row in excel_data.iterrows():
        source = row.get('Source', '')
        if not source:
            empty_source += 1
            continue

        query = clean_url(source)
        if not query:
            skipped_rows += 1
            continue

        if query in cleaned_data:
            duplicate_cleaned_urls += 1
            print(f"Дубликат: {source} -> {query}")
            continue

        cleaned_data[query] = {
            'Source': source,
            'Signal': row.get('Signal', ''),
            'Signal presence': row.get('Signal presence', '')
        }

    print(f"Загружено {len(cleaned_data)} строк из Excel файла")
    print(f"Пропущено строк с пустым Source: {empty_source}")
    print(f"Пропущено строк с пустым очищенным URL: {skipped_rows}")
    print(f"Пропущено дубликатов очищенных URL: {duplicate_cleaned_urls}")

    with codecs.open(target_csv, 'r', encoding=target_encoding) as infile, \
         codecs.open(output_csv, 'w', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Source', 'Signal', 'Signal presence']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        rows_processed = 0
        matched_count = 0
        total_rows = sum(1 for row in csv.DictReader(codecs.open(target_csv, 'r', encoding=target_encoding)))
        print(f"Всего строк в целевом CSV: {total_rows}")

        infile.seek(0)  # Reset file pointer
        next(reader)  # Skip header

        for row in reader:
            rows_processed += 1
            website = clean_url(row.get('Website', ''))
            company_name = row.get('Company', '')
            
            matched_data = cleaned_data.get(website)
            
            if matched_data:
                row['Source'] = matched_data['Source']
                row['Signal'] = matched_data['Signal']
                row['Signal presence'] = matched_data['Signal presence']
                matched_count += 1
                if rows_processed <= 10 or rows_processed % 100 == 0:
                    print_debug_info(rows_processed, website, matched_data, True, company_name)
            else:
                row['Source'] = 'N/A'
                row['Signal'] = 'N/A'
                row['Signal presence'] = 'N/A'
                
                if rows_processed <= 10 or rows_processed % 100 == 0:
                    print(f"\nНе найдено совпадение для строки {rows_processed}:")
                    print(f"Website: {website}")
                    print(f"Company name: {company_name}")

            writer.writerow(row)

            if rows_processed % 100 == 0:
                print(f"Обработано строк: {rows_processed}, Совпадений найдено: {matched_count}")

    end_time = time.time()
    processing_time = end_time - start_time

    print(f"Обработка завершена. Результаты сохранены в файл: {output_csv}")
    print(f"Всего строк обработано: {rows_processed}")
    print(f"Строк с найденными совпадениями: {matched_count}")
    print(f"Время обработки: {processing_time:.2f} секунд")

if __name__ == "__main__":
    excel_file = "/home/pavel/Signal enricher/output_file.xlsx"
    target_csv = "/home/pavel/Signal enricher/apollo_export.csv"
    output_csv = "/home/pavel/Signal enricher/pharma_final.csv"
    
    process_pharma_data(excel_file, target_csv, output_csv)