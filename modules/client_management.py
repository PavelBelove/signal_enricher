# modules/client_management.py

import os
import json
from datetime import datetime

def create_project_structure(config):
    client_name = config['client_name']
    search_date = datetime.now()

    # Корневая папка проекта
    project_root = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(project_root)  # Поднимаемся на уровень выше

    # Папка результатов
    results_dir = os.path.join(project_root, 'results')
    os.makedirs(results_dir, exist_ok=True)

    # Папка клиента
    client_dir = os.path.join(results_dir, client_name)
    os.makedirs(client_dir, exist_ok=True)

    # Папка ролей
    roles_dir = os.path.join(client_dir, 'roles')
    os.makedirs(roles_dir, exist_ok=True)

    # Файлы в папке ролей
    prompt_file = os.path.join(roles_dir, 'prompt.txt')
    search_query_file = os.path.join(roles_dir, 'search_query.json')

    with open(prompt_file, 'w') as f:
        f.write(config['prompt'])

    with open(search_query_file, 'w') as f:
        json.dump(config['search_queries'], f)

    # Папка текущего поиска
    search_date_str = search_date.strftime('%Y-%m-%d')
    current_search_dir = os.path.join(client_dir, search_date_str)
    os.makedirs(current_search_dir, exist_ok=True)

    # Создание пустых файлов для текущего поиска
    files_in_search = [
        'search_results.csv',
        'search_results_cleaned.csv',
        'search_results_analysed.csv'
    ]
    for file in files_in_search:
        open(os.path.join(current_search_dir, file), 'w').close()

    print(f"Структура папок и файлов создана для клиента '{client_name}' и даты '{search_date_str}'.")

def select_client():
    clients_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
    clients = [d for d in os.listdir(clients_dir) if os.path.isdir(os.path.join(clients_dir, d))]

    print("Доступные клиенты:")
    for i, client in enumerate(clients):
        print(f"{i + 1}. {client}")

    client_index = int(input("Выберите клиента (введите номер): ")) - 1
    return clients[client_index]

def get_client_and_date():
    print("1. Создать нового клиента")
    print("2. Выбрать существующего клиента")
    choice = int(input("Выберите действие (введите номер): "))

    if choice == 1:
        with open('config/new_client_profile.json', 'r') as f:
            config = json.load(f)
        create_project_structure(config)
        client_name = config['client_name']
        search_date = datetime.now()
    elif choice == 2:
        client_name = select_client()
        search_date_str = input("Введите дату поиска (в формате YYYY-MM-DD): ")
        search_date = datetime.strptime(search_date_str, '%Y-%m-%d')
    else:
        print("Неверный выбор")
        return None, None

    return client_name, search_date