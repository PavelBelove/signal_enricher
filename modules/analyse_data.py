# modules/analyse_data.py

import os
import pandas as pd
from openpyxl import load_workbook
from modules.utils import load_role_description, signal_handler, gpt_query

# Функция для анализа данных
def analyse_data(input_filename, output_filename, roles_dir):
    # Путь к файлу с ролями
    role_file = os.path.join(roles_dir, 'prompt.txt')

    # Загрузка описания роли
    role_description = load_role_description(role_file)

    # Загрузка данных из CSV
    df = pd.read_csv(input_filename)

    # Добавление колонки для результатов анализа
    df['analysis'] = ""

    # Счетчик использованных токенов
    tokens_used_total = 0

    # Анализ данных
    for index, row in df.iterrows():
        full_article_text = row['description'] or ""
        try:
            if len(full_article_text) >= 100:
                # Обрезаем текст, если он слишком длинный
                if len(full_article_text) > 2000:
                    full_article_text = full_article_text[:2000]

                # Анализ полного текста статьи
                article_messages = [
                    {"role": "system", "content": role_description},
                    {"role": "user", "content": full_article_text}
                ]
                answer_article, tokens_used_article = gpt_query(article_messages)
                tokens_used_total += tokens_used_article

                # Вывод результатов анализа и использованных токенов
                print(f"Строка {index + 1}:")
                print(f" Ответ анализа содержания статьи: {answer_article}")
                print(f" Использовано токенов для статьи: {tokens_used_article}")

                # Запись результата в DataFrame
                df.at[index, 'analysis'] = answer_article
            else:
                print(f"Строка {index + 1}: текст статьи слишком короткий для анализа. {full_article_text}")
        except Exception as e:
            print(f"Ошибка при обработке строки {index + 1}: {e}")

    # Сохранение результатов анализа в CSV
    df.to_csv(output_filename, index=False)
    print(f"Обработка завершена. Общее количество использованных токенов: {tokens_used_total}")
    print(f"Результаты сохранены в '{output_filename}'.")

if __name__ == "__main__":
    # Пример использования
    input_filename = 'results/example_client/2024-06-13/search_results_cleaned.csv'
    output_filename = 'results/example_client/2024-06-13/search_results_analysed.csv'
    roles_dir = 'results/example_client/roles'
    analyse_data(input_filename, output_filename, roles_dir)