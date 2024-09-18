import os
import pandas as pd
import asyncio
import time
from modules.utils import gpt_query_async, load_role_description

class RateLimiter:
    def __init__(self, max_rate, period=60):
        self.max_rate = max_rate
        self.period = period
        self.tokens = max_rate
        self.updated_at = time.monotonic()

    async def acquire(self):
        while True:
            now = time.monotonic()
            time_passed = now - self.updated_at
            self.tokens += time_passed * (self.max_rate / self.period)
            if self.tokens > self.max_rate:
                self.tokens = self.max_rate
            self.updated_at = now

            if self.tokens >= 1:
                self.tokens -= 1
                return
            
            sleep_time = (1 - self.tokens) / (self.max_rate / self.period)
            await asyncio.sleep(sleep_time)

async def analyse_data(input_filename, output_filename, roles_dir):
    # Путь к файлу с ролями
    role_file = os.path.join(roles_dir, 'prompt.txt')

    # Загрузка описания роли
    role_description = load_role_description(role_file)

    # Загрузка данных из CSV
    print(f"Загрузка данных из {input_filename}...")
    df = pd.read_csv(input_filename)
    print(f"Загружено {len(df)} строк.")

    # Если колонки 'analysis' нет, добавляем ее
    if 'analysis' not in df.columns:
        df['analysis'] = ""

    # Счетчик использованных токенов
    tokens_used_total = 0

    # Создание ограничителя скорости: 20 запросов в минуту
    rate_limiter = RateLimiter(max_rate=20)

    # Создание семафора для ограничения одновременных запросов
    semaphore = asyncio.Semaphore(20)

    async def process_row(index, row):
        nonlocal tokens_used_total
        try:
            # Проверяем, не был ли уже проанализирован этот ряд
            if pd.isna(row['analysis']) or row['analysis'] == "":
                # Подготовка текста для анализа
                full_article_text = ""
                
                # Добавляем имя компании, если оно есть
                if 'Organization name' in row and pd.notna(row['Organization name']):
                    full_article_text += f"Company: {row['Organization name']}\n"
                
                # Добавляем вебсайт, если он есть
                if 'Website' in row and pd.notna(row['Website']):
                    full_article_text += f"Website: {row['Website']}\n"
                
                # Добавляем основной текст статьи
                if pd.notna(row['description']):
                    full_article_text += str(row['description'])
                
                # Удаление начальных и конечных пробелов
                full_article_text = full_article_text.strip()

                if len(full_article_text) >= 100:
                    # Обрезаем текст, если он слишком длинный
                    if len(full_article_text) > 5000:
                        full_article_text = full_article_text[:5000]
                    
                    article_messages = [
                        {"role": "system", "content": role_description},
                        {"role": "user", "content": full_article_text}
                    ]
                    
                    async with semaphore:
                        # Ожидание разрешения от ограничителя скорости
                        await rate_limiter.acquire()
                        
                        answer_article, tokens_used_article = await gpt_query_async(article_messages)
                    
                    tokens_used_total += tokens_used_article

                    # Вывод результатов анализа и использованных токенов
                    print(f"\nСтрока {index + 1}:")
                    print(f"Использовано токенов: {tokens_used_article}")
                    print(f"Результат анализа: {answer_article[:600]}...")  # Вывод первых 600 символов

                    # Запись результата в DataFrame
                    df.at[index, 'analysis'] = answer_article
                else:
                    print(f"\nСтрока {index + 1}: текст статьи слишком короткий для анализа. Длина: {len(full_article_text)}")
            else:
                print(f"\nСтрока {index + 1}: анализ уже проведен ранее.")
        
        except Exception as e:
            print(f"\nОшибка при обработке строки {index + 1}: {e}")
        
        # Сохранение результатов после обработки каждой строки
        df.to_csv(output_filename, index=False)
        print(f"Результаты сохранены в '{output_filename}'. Обработано {index + 1} строк.")

    # Создание и запуск задач для каждой строки
    tasks = [process_row(index, row) for index, row in df.iterrows()]
    await asyncio.gather(*tasks)

    print(f"\nВсего использовано токенов: {tokens_used_total}")
    print(f"Анализ завершен. Результаты сохранены в '{output_filename}'.")

# Функция-обертка для запуска асинхронной функции
def run_analyse_data(input_filename, output_filename, roles_dir):
    asyncio.run(analyse_data(input_filename, output_filename, roles_dir))