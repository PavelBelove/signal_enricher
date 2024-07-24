import json
from typing import List, Optional
from modules.fetch_data import fetch_xmlstock_search_results
from modules.link_utils import find_best_link
from modules.bing_search import get_bing_search_results

def load_config():
    with open('config/search_config.json', 'r') as f:
        return json.load(f)

def find_link(post_text: str, time_flag: str) -> Optional[str]:
    config = load_config()
    search_query = ' '.join(post_text.split()[:config['link_finder']['max_words']])
    linkedin_query = f"{search_query} site:linkedin.com"
    print(f"Поиск ссылки для текста: {linkedin_query[:50]}...")
    
    for engine in config['search_engines']:
        if engine['enabled']:
            print(f"Использование поисковой системы: {engine['name']}")
            if engine['name'] == 'xmlsearch':
                results = fetch_xmlstock_search_results(
                    linkedin_query,
                    config['days'], 
                    config['num_results'], 
                    config['num_pages'], 
                    config['sites'],
                    verbose=False
                )
            elif engine['name'] == 'bing':
                results = get_bing_search_results(linkedin_query, engine)
            else:
                # Для будущих поисковых систем
                results = []

            if results:
                best_link = find_best_link([result['link'] for result in results])
                if best_link != "N/A":
                    print(f"Найдена лучшая ссылка через {engine['name']}: {best_link}")
                    return best_link
                else:
                    print(f"Подходящая ссылка не найдена через {engine['name']}")
            else:
                print(f"Ссылка не найдена через {engine['name']}")
    
    print("Подходящая ссылка не найдена ни в одной поисковой системе")
    return "N/A"

def update_missing_links(data: List[dict]) -> List[dict]:
    config = load_config()
    time_flags = [flag.lower() for flag in config['link_finder']['time_flags']]
    
    for i, item in enumerate(data):
        # print(f"Обработка записи {i+1}/{len(data)}")
        if item['link'] == "N/A" and item['time'].lower() in time_flags:
            item['link'] = find_link(item['description'], item['time'])
    
    return data