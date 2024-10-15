import sys
sys.path.append('.')  # Добавляем текущую директорию в путь поиска модулей

from modules.fetch_data import fetch_and_parse

def test_article_scraping(url):
    print(f"Тестирование извлечения текста со страницы: {url}")
    result = fetch_and_parse(url, verbose=True)
    
    print("\nРезультаты:")
    print(f"Заголовок: {result['title']}")
    print(f"Авторы: {', '.join(result['authors'])}")
    print(f"Текст (первые 500 символов):\n{result['text'][:500]}...")
    
    if result['text'] == "Таймаут при получении статьи" or result['text'].startswith("Ошибка при"):
        print("\nНе удалось извлечь текст статьи.")
    else:
        print(f"\nУспешно извлечен текст длиной {len(result['text'])} символов.")

if __name__ == "__main__":
    url = "https://www.crunchbase.com/organization/g-core-labs"
    test_article_scraping(url)