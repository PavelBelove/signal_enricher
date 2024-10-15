# llm_clients/openai_client.py

import asyncio
import os
from typing import List, Dict, Any, Callable, AsyncGenerator
from itertools import cycle
import logging
import openai

from .base_client import BaseLLMClient

class OpenAIClient(BaseLLMClient):
    """
    Клиент для работы с OpenAI API с балансировкой ключей и обработкой исчерпанных ключей.
    """

    EXHAUSTED_MARKER = "#EXHAUSTED#"

    def __init__(self, config: Dict[str, Any]):
        self.model = config.get('model', 'gpt-4o-mini')  # По умолчанию gpt-4o-mini
        self.max_retries = config.get('max_retries', 5)
        self.retry_delay = config.get('retry_delay', 1)  # в секундах
        self.timeout = config.get('timeout', 60)  # в секундах
        self.max_tokens = config.get('max_tokens', 1500)
        self.temperature = config.get('temperature', 0.7)
        self.top_p = config.get('top_p', 0.9)
        self.rate_limit = config.get('rate_limit', 20)  # Запросов в минуту
        self.rate_limit_period = config.get('rate_limit_period', 60)  # Период в секундах

        # Установка ключей API из переменных окружения
        self.api_keys_env = os.getenv('OPENAI_API_KEYS')
        if not self.api_keys_env:
            raise ValueError("Переменная окружения OPENAI_API_KEYS не установлена.")

        # Ожидаем, что ключи передаются через запятую
        self.api_keys_list = [key.strip() for key in self.api_keys_env.split(',') if key.strip()]
        if not self.api_keys_list:
            raise ValueError("Переменная окружения OPENAI_API_KEYS не содержит ни одного ключа.")

        self.api_keys = cycle(self.api_keys_list)
        self.current_key = next(self.api_keys)

        openai.api_key = self.current_key

    def _mark_key_as_exhausted(self, key: str):
        logging.warning(f"Помечен ключ как исчерпанный: {key}")
        self.api_keys_list = [k for k in self.api_keys_list if k != key]
        if not self.api_keys_list:
            raise ValueError("Все API ключи исчерпаны.")
        self.api_keys = cycle(self.api_keys_list)
        self.current_key = next(self.api_keys)
        openai.api_key = self.current_key

    async def _handle_api_call(self, api_call: Callable):
        for attempt in range(self.max_retries):
            try:
                return await api_call()
            except openai.error.RateLimitError as e:
                logging.error(f"Rate limit error: {e}. Переход на следующий ключ.")
                self._mark_key_as_exhausted(self.current_key)
                self.current_key = next(self.api_keys)
                openai.api_key = self.current_key
            except openai.error.APIError as e:
                logging.error(f"Ошибка API: {e}")
                if attempt == self.max_retries - 1:
                    raise
                logging.info(f"Повторная попытка {attempt + 1} через {self.retry_delay} секунд.")
                await asyncio.sleep(self.retry_delay * (attempt + 1))
            except Exception as e:
                logging.error(f"Общая ошибка: {e}")
                if attempt == self.max_retries - 1:
                    raise
                logging.info(f"Повторная попытка {attempt + 1} через {self.retry_delay} секунд.")
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    async def get_completion(self, messages: List[Dict[str, str]]) -> str:
        async def api_call():
            # Используем asyncio.to_thread для выполнения синхронного вызова OpenAI в асинхронной функции
            return await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p
            )

        response = await self._handle_api_call(api_call)
        return response.choices[0].message['content']

    async def get_completion_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        async def api_call():
            return await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                stream=True
            )

        async for chunk in await self._handle_api_call(api_call):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
