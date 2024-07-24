import os
import csv
from bs4 import BeautifulSoup
import logging
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_html_file(file_path):
    logging.info(f"Парсинг файла: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            posts = []

            # Извлечение query из имени файла
            file_name = os.path.basename(file_path)
            query_match = re.search(r'(.+?) \* Поиск \* LinkedIn\.html', file_name)
            query = query_match.group(1) if query_match else ""

            # Поиск всех постов
            all_posts = soup.find_all('div', class_='feed-shared-update-v2')
            logging.info(f"Найдено постов: {len(all_posts)}")

            for post in all_posts:
                try:
                    # Извлечение текста поста (description)
                    text_element = post.find('span', class_='break-words')
                    description = ' '.join(text_element.stripped_strings) if text_element else ''
                    logging.info(f"Текст поста: {description[:50]}...")  # Вывод первых 50 символов

                    # Извлечение информации об авторе (title) и ссылки на автора (link)
                    author_element = post.find('a', class_='app-aware-link update-components-actor__meta-link')
                    if author_element:
                        title = author_element.find('span', class_='update-components-actor__name').get_text(strip=True)
                        link = author_element.get('href', '')
                        logging.info(f"Автор (title): {title}")
                        logging.info(f"Ссылка на автора (link): {link}")
                    else:
                        title = ''
                        link = ''
                        logging.warning("Информация об авторе не найдена")

                    # Добавление pubDate (пустое значение, так как нет в исходных данных)
                    pubDate = ''

                    posts.append({
                        'title': title,
                        'link': link,
                        'pubDate': pubDate,
                        'description': description,
                        'query': query
                    })

                except Exception as e:
                    logging.error(f"Ошибка при обработке поста: {str(e)}")

            return posts
    except Exception as e:
        logging.error(f"Ошибка при открытии или парсинге файла {file_path}: {str(e)}")
        return []

def main():
    html_folder = 'linkedin_parser/HTML'
    output_file = 'search_results.csv'

    all_posts = []

    # Проход по всем HTML файлам в папке
    for filename in os.listdir(html_folder):
        if filename.endswith('.html'):
            file_path = os.path.join(html_folder, filename)
            file_posts = parse_html_file(file_path)
            all_posts.extend(file_posts)
            logging.info(f"Обработано постов в файле {filename}: {len(file_posts)}")

    logging.info(f"Всего обработано постов: {len(all_posts)}")

    # Запись результатов в CSV файл
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'link', 'pubDate', 'description', 'query']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for post in all_posts:
            writer.writerow(post)

    logging.info(f"Парсинг завершен. Результаты сохранены в {output_file}")

if __name__ == "__main__":
    main()