import csv
import json
import requests
import os
from typing import List, Dict

def load_config(config_path: str) -> Dict:
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def get_enriched_data(api_key: str, company_name: str, job_titles: List[str]) -> List[Dict]:
    apollo_api_url = "https://api.apollo.io/v1/people/search"
    all_contacts = []

    for job_title in job_titles:
        params = {
            "api_key": api_key,
            "q_company": company_name,
            "q_title": job_title,
            "page": 1
        }

        try:
            response = requests.get(apollo_api_url, params=params)
            response.raise_for_status()
            data = response.json()
            contacts = data.get('people', [])
            all_contacts.extend(contacts)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {company_name} - {job_title}: {e}")
            print(f"Request URL: {response.url}")
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")

    return all_contacts

def create_enriched_row(original_row: Dict, contact: Dict, contact_fields: List[str]) -> Dict:
    enriched_row = original_row.copy()
    for field in contact_fields:
        if field == 'name':
            enriched_row[field] = contact.get(field, 'N/A')
        elif field == 'title':
            enriched_row[field] = contact.get(field, 'N/A')
        elif field == 'email':
            enriched_row[field] = contact.get(field, 'N/A')
        elif field == 'phone':
            enriched_row[field] = contact.get('phone_number', 'N/A')
        elif field == 'linkedin_url':
            enriched_row[field] = contact.get(field, 'N/A')
    return enriched_row

def enrich_leads(input_csv: str, output_csv: str, config_path: str, api_key: str):
    config = load_config(config_path)
    
    with open(input_csv, 'r') as input_file, open(output_csv, 'w', newline='') as output_file:
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames + config['contact_fields']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            company_name = row['company_name']  # Предполагаем, что в CSV есть колонка 'company_name'
            contacts = get_enriched_data(api_key, company_name, config['titles'])

            if not contacts:
                enriched_row = row.copy()
                for field in config['contact_fields']:
                    enriched_row[field] = 'N/A'
                writer.writerow(enriched_row)
            else:
                for contact in contacts:
                    enriched_row = create_enriched_row(row, contact, config['contact_fields'])
                    writer.writerow(enriched_row)

    print(f"Enriched data saved to {output_csv}")

if __name__ == "__main__":
    # Получаем API ключ из переменной окружения
    api_key = os.environ.get('APOLLO_API_KEY')
    if not api_key:
        raise ValueError("APOLLO_API_KEY not found in environment variables")

    # Тестовый запрос
    test_company = "Armour Construction Consultants"
    test_titles = ["Owner", "Partner", "Chief Executive Officer"]

    print(f"Testing API call for {test_company}...")
    contacts = get_enriched_data(api_key, test_company, test_titles)

    if contacts:
        print(f"Found {len(contacts)} contacts:")
        for contact in contacts:
            print(f"Name: {contact.get('name', 'N/A')}")
            print(f"Title: {contact.get('title', 'N/A')}")
            print(f"Email: {contact.get('email', 'N/A')}")
            print(f"Phone: {contact.get('phone_number', 'N/A')}")
            print(f"LinkedIn: {contact.get('linkedin_url', 'N/A')}")
            print("---")
    else:
        print("No contacts found.")

    # Пример использования функции enrich_leads
    # enrich_leads('input_leads.csv', 'enriched_leads.csv', 'config.json', api_key)