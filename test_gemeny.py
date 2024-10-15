import time
import requests

# Импортируем API-ключи из файла
from config.api_keys import api_keys

# API URL, который вы хотите протестировать (замените на нужный вам)
API_URL = "https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText"

# Параметры запроса (замените на нужные для вашего API)
data = {
    "prompt": "Test",
    "model": "text-bison-001"
}

# Функция для тестирования ключа
def test_api_key(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            print(f"Ключ {api_key[:10]}... работает: {response.json()}")
        elif response.status_code == 403:
            print(f"Ключ {api_key[:10]}... не имеет доступа: {response.json()}")
        elif response.status_code == 429:
            print(f"Ключ {api_key[:10]}... превысил лимиты: {response.json()}")
        else:
            print(f"Ключ {api_key[:10]}... вызвал ошибку {response.status_code}: {response.json()}")
    except Exception as e:
        print(f"Ошибка с ключом {api_key[:10]}...: {str(e)}")

# Основная функция для тестирования всех ключей
def test_all_api_keys(api_keys, delay=2):
    for api_key in api_keys["gemini_api_keys"]:
        test_api_key(api_key)
        time.sleep(delay)  # Задержка между запросами для предотвращения превышения лимита

if __name__ == "__main__":
    test_all_api_keys(api_keys, delay=2)
