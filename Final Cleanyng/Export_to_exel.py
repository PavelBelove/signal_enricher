import csv
import ast
import re
from openpyxl import Workbook

def safe_literal_eval(val):
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        return val

def clean_text(text):
    return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', str(text))

def truncate_text(text, max_length=10000):
    return text[:max_length] if len(text) > max_length else text

def format_value(value):
    if isinstance(value, str) and value:
        return value[0].upper() + value[1:].lower()
    return value

def clean_linkedin_link(link):
    if "linkedin.com" in link:
        return link.split('?')[0]
    return link

def process_csv_to_excel(input_csv, output_excel):
    wb = Workbook()
    ws = wb.active
    ws.title = "Processed Data"

    headers = ["Mentioned Company", "Signal (True/False)", 
               "Event Time", "Source Link", "Text"]
    ws.append(headers)

    with open(input_csv, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            analysis = safe_literal_eval(row['analysis'])
            
            if isinstance(analysis, list) and len(analysis) == 3:
                company = clean_text(analysis[0])
                signal = format_value(str(analysis[1]))
                time = format_value(str(analysis[2]))
            else:
                company = "N/A"
                signal = "N/A"
                time = "N/A"
            
            link = clean_linkedin_link(clean_text(row.get('link', 'N/A')))
            description = clean_text(row.get('description', 'N/A'))
            description = truncate_text(description, 10000)

            ws.append([company, signal, time, link, description])

    wb.save(output_excel)
    print(f"Excel file successfully created: {output_excel}")

# Usage
input_csv = "results/designers/2024-07-17-web/search_results_analysed.csv"  # Replace with the path to your input CSV file
output_excel = "output.xlsx"  # Replace with the desired path for your output Excel file

process_csv_to_excel(input_csv, output_excel)