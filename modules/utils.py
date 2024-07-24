import os
import sys
import re
import openai
import google.generativeai as genai
import pandas as pd 
import time
from functools import wraps
from config.api_keys import api_keys
import json

# Load the configuration
with open('config/search_config.json', 'r') as f:
    config = json.load(f)

use_gemeni = config.get("use_gemeni", True)
gemeni_rate_limit = config.get("gemeni_rate_limit")
gemeni_api_key = api_keys["gemeni_api_key"]

# Configure Gemini API
if use_gemeni:
    genai.configure(api_key=gemeni_api_key)

def load_role_description(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def signal_handler(sig, frame, workbook, filename, verbose=False):
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
    if use_gemeni:
        # Gemeni API request
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare the prompt
        prompt = f"System: {messages[0]['content']}\nHuman: Analyze the following article:\n\n{messages[1]['content']}"
        
        try:
            response = model.generate_content(prompt)
            content = response.text
            tokens_used = len(prompt.split()) + len(content.split())  # Simple token estimation
            return content, tokens_used
        except Exception as e:
            print(f"Error in Gemini API request: {e}")
            return str(e), 0

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
    df = pd.DataFrame(results)
    df.to_csv(output_filename, index=False)
    if verbose:
        print(f"Результаты успешно сохранены в файл: {output_filename}")

def clean_text(text):
    """Очищает текст от нежелательных символов."""
    return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', str(text))

def format_value(value):
    """Форматирует значение, делая первую букву заглавной."""
    if isinstance(value, str) and value:
        return value[0].upper() + value[1:].lower()
    return value

def truncate_text(text, max_length=10000):
    """Обрезает текст до заданной максимальной длины."""
    return text[:max_length] if len(text) > max_length else text

def clean_linkedin_link(link):
    """Очищает ссылку LinkedIn от дополнительных параметров."""
    if "linkedin.com" in link:
        return link.split('?')[0]
    return link