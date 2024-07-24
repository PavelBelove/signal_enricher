import os
import pandas as pd
from modules.utils import gpt_query, load_role_description

def analyse_data(input_filename, output_filename, roles_dir):
    # Путь к файлу с ролями
    role_file = os.path.join(roles_dir, 'prompt.txt')

    # Загрузка описания роли
    role_description = load_role_description(role_file)

    # Загрузка данных из CSV
    print(f"Loading data from {input_filename}...")
    df = pd.read_csv(input_filename)
    print(f"Loaded {len(df)} rows.")

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
                print(f"Querying model for row {index + 1}...")
                answer_article, tokens_used_article = gpt_query(article_messages)  # Убран аргумент proxy
                tokens_used_total += tokens_used_article

                # Вывод результатов анализа и использованных токенов
                print(f"Row {index + 1}:")
                print(f" Analysis response: {answer_article[:100]}...")  # Print first 100 characters
                print(f" Tokens used for article: {tokens_used_article}")

                # Запись результата в DataFrame
                df.at[index, 'analysis'] = answer_article
            else:
                print(f"Row {index + 1}: article text too short for analysis. Length: {len(full_article_text)}")
        except Exception as e:
            print(f"Error processing row {index + 1}: {e}")
        
        # Save results after each processed row
        df.to_csv(output_filename, index=False)
        print(f"Results saved to '{output_filename}'. Processed {index + 1} rows.")

    print(f"Total tokens used: {tokens_used_total}")
    print(f"Analysis complete. Results saved to '{output_filename}'.")

    print(f"Processing completed. Total tokens used: {tokens_used_total}")
    print(f"Final results saved to '{output_filename}'.")