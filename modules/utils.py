import os
import sys
import signal
import openai
import google.generativeai as genai
import pandas as pd 
import time
from functools import wraps
from config.api_keys import api_keys
import json

# Set the OpenAI API key
openai.api_key = api_keys["openai_api_key"]

# Load the configuration
with open('config/search_config.json', 'r') as f:
    config = json.load(f)

use_gemeni = config.get("use_gemeni", False)
gemeni_rate_limit = config.get("gemeni_rate_limit")
gemeni_api_key = api_keys["gemeni_api_key"]


# Configure Gemini API
if use_gemeni:
    genai.configure(api_key=gemeni_api_key)

def load_role_description(file_path):
    """
    Load the role description from a file.

    Args:
        file_path (str): Path to the file containing the role description.

    Returns:
        str: The role description text.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def signal_handler(sig, frame, workbook, filename, verbose=False):
    """
    Signal handler for saving and closing the workbook on interrupt.

    Args:
        sig (int): Signal number.
        frame (frame): Current stack frame.
        workbook (Workbook): Workbook object to save and close.
        filename (str): Path to the file to save the workbook.
        verbose (bool): Flag to enable/disable verbose output.
    """
    if verbose:
        print('You pressed Control+C! Saving and closing the file...')
    workbook.save(filename)
    workbook.close()
    sys.exit(0)

def rate_limiter(max_per_minute):
    min_interval = 60.0 / max_per_minute
    last_called = [0.0]

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorate

@rate_limiter(gemeni_rate_limit)
def gpt_query(messages):
    """
    Query the GPT-4 model or Gemeni model based on configuration.

    Args:
        messages (list): List of messages to send to the model.

    Returns:
        tuple: A tuple containing the response content and the number of tokens used.
    """
    if use_gemeni:
        # Gemeni API request
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare the prompt
        prompt = f"System: {messages[0]['content']}\nHuman: Analyze the following article:\n\n{messages[1]['content']}"
        
        response = model.generate_content(prompt)
        content = response.text
        tokens_used = len(prompt.split()) + len(content.split())  # Простая оценка количества токенов
        return content, tokens_used
    else:
        # OpenAI GPT-4 API request
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=100,
            temperature=0.3
        )
        content = response.choices[0].message['content']
        tokens_used = response['usage']['total_tokens']
        return content, tokens_used

def save_results_to_csv(results, output_filename, verbose=False):
    """
    Сохраняет результаты в файл CSV.

    :param results: список словарей с результатами
    :param output_filename: имя выходного файла CSV
    :param verbose: флаг для вывода отладочной информации
    """
    # Создаем DataFrame из списка результатов
    df = pd.DataFrame(results)

    # Сохраняем DataFrame в файл CSV
    df.to_csv(output_filename, index=False)

    if verbose:
        print(f"Результаты успешно сохранены в файл: {output_filename}")



