# quantum_rpg_bot/llm_clients/gemini_client.py

import asyncio
import google.generativeai as genai
from typing import List, Dict, Any, Callable
# from config import Config
from .base_client import BaseLLMClient
from itertools import cycle

class GeminiClient(BaseLLMClient):
    """
    Клиент для работы с Gemini Pro с поддержкой нескольких API ключей.
    Обеспечивает балансировку нагрузки и обратную совместимость с существующим кодом.
    """

    def __init__(self, config: Config):
        self.api_keys = config.GEMINI_API_KEYS
        self.key_cycle = cycle(self.api_keys)
        self.max_retries = config.MAX_RETRIES
        self.retry_delay = config.RETRY_DELAY
        self.timeout = config.GPT_TIMEOUT

    def _get_model(self):
        """
        Создает и возвращает новую модель с следующим API ключом из цикла.
        """
        key = next(self.key_cycle)
        print(f"Использован ключ {key}")
        genai.configure(api_key=key)
        return genai.GenerativeModel('gemini-pro')

    @property
    def model(self):
        """
        Свойство для обеспечения обратной совместимости.
        Возвращает новую модель при каждом обращении.
        """
        return self._get_model()

    async def get_completion(self, messages: List[Dict[str, str]], update_callback: Callable[[], Any] = None) -> str:
        prompt = self._format_messages(messages)
        for attempt in range(self.max_retries):
            try:
                model = self._get_model()
                response = await asyncio.wait_for(
                    model.generate_content_async(prompt),
                    timeout=self.timeout
                )
                return response.text
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                if update_callback:
                    await update_callback()
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    async def get_completion_stream(self, messages: List[Dict[str, str]], update_callback: Callable[[], Any] = None):
        prompt = self._format_messages(messages)
        for attempt in range(self.max_retries):
            try:
                model = self._get_model()
                response = await model.generate_content_async(prompt, stream=True)
                async for chunk in response:
                    yield chunk.text
                return
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                if update_callback:
                    await update_callback()
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Форматирует сообщения в строку для Gemini Pro.
        """
        formatted_messages = []
        for message in messages:
            role = message['role']
            content = message['content']
            formatted_messages.append(f"{role.capitalize()}: {content}")
        return "\n".join(formatted_messages)