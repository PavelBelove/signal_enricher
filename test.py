import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from modules.date_utils import parse_date
from config.api_keys import api_keys

# Данные для авторизации в API
user = api_keys["xmlstock_user"]
key = api_keys["xmlstock_key"]
url = "https://xmlstock.com/google/xml/"

# Семафор для ограничения количества одновременных запросов
semaphore = asyncio.Semaphore(10)

async def fetch_xmlstock_search_results(query, config, verbose=True):
    """
    Асинхронно получает результаты поиска из API xmlstock.
    """
    results = []
    full_query = query  # Используем только сам запрос
    
    # Эмуляция конфигурации поисковой системы
    xmlsearch_config = {
        "name": "xmlsearch",
        "groupby": 10,
        "num_results": 10,
        "num_pages": 1,
        "domain": "",
        "tbm": "",
        "hl": "en",
        "device": "",
        "lr": "",
        "days": 365
    }

    params = {
        "user": user,
        "key": key,
        "query": full_query,
        "groupby": min(max(xmlsearch_config['num_results'], 10), 100),
        "sort": "date"
    }
    
    # Добавляем параметры из конфигурации
    for param in ['domain', 'tbm', 'hl', 'device', 'lr']:
        if xmlsearch_config.get(param):
            params[param] = xmlsearch_config[param]
    
    # Добавляем фильтр по дням, если он указан
    if xmlsearch_config['days']:
        params["tbs"] = f"qdr:d{xmlsearch_config['days']}"
    
    async with aiohttp.ClientSession() as session:
        for page in range(xmlsearch_config['num_pages']):
            params['page'] = page
            if verbose:
                print(f"Отправка запроса с параметрами: {params}")
            
            async with semaphore:  # Ограничиваем одновременные запросы
                try:
                    async with session.get(url, params=params, timeout=30) as response:
                        if verbose:
                            print(f"Код статуса ответа: {response.status}")
                            print(f"URL запроса: {response.url}")
                        
                        if response.status != 200:
                            print(f"Ошибка при получении результатов: {response.status}")
                            print(await response.text())
                            continue

                        content = await response.text()
                        print(f"Полученный XML: {content[:500]}...")  # Выводим первые 500 символов XML для проверки
                        
                        # Парсинг XML ответа
                        root = ET.fromstring(content)
                        for group in root.findall('.//group'):
                            for doc in group.findall('doc'):
                                pub_date = doc.find('pubDate').text if doc.find('pubDate') is not None else "N/A"
                                pub_date_dt = parse_date(pub_date) if pub_date != "N/A" else None
                                
                                # Фильтруем по дате, если указано
                                if xmlsearch_config['days'] is False or (pub_date_dt is not None and pub_date_dt >= (datetime.now() - timedelta(days=xmlsearch_config['days']))):
                                    result = {
                                        'title': doc.find('title').text if doc.find('title') is not None else "N/A",
                                        'link': doc.find('url').text if doc.find('url') is not None else "N/A",
                                        'pubDate': pub_date
                                    }
                                    results.append(result)
                                    print(f"Найден результат: {result}")

                                    # Лимитируем количество результатов
                                    if len(results) >= xmlsearch_config['num_results']:
                                        return results[:xmlsearch_config['num_results']]
                    
                    print(f"Количество полученных результатов: {len(results)}")
                
                except asyncio.TimeoutError:
                    print(f"Таймаут при получении результатов для страницы {page}")
                except Exception as e:
                    print(f"Ошибка при получении результатов для страницы {page}: {e}")
                
                await asyncio.sleep(1)  # Задержка между запросами

    return results[:xmlsearch_config['num_results']]


# Тестовая функция для вызова
def test_fetch():
    query = "Two Circles investments"  # Пример запроса
    config = {
        "search_engines": [
            {
                "name": "xmlsearch",
                "num_results": 10,
                "num_pages": 1,
                "days": 365
            }
        ]
    }
    
    # Запуск асинхронного вызова
    asyncio.run(fetch_xmlstock_search_results(query, config))

# Вызов тестовой функции
if __name__ == "__main__":
    test_fetch()
