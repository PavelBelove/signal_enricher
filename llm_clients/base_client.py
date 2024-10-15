# quantum_rpg_bot/llm_clients/base_client.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable, AsyncGenerator

class BaseLLMClient(ABC):
    """
    Базовый абстрактный класс для клиентов языковых моделей.
    """

    @abstractmethod
    async def get_completion(self, messages: List[Dict[str, str]], update_callback: Callable[[], Any] = None) -> str:
        """
        Получает завершение от языковой модели.

        Args:
            messages (List[Dict[str, str]]): Список сообщений для отправки модели.
            update_callback (Callable[[], Any], optional): Функция обратного вызова для обновления статуса.

        Returns:
            str: Ответ от языковой модели.
        """
        pass

    @abstractmethod
    async def get_completion_stream(self, messages: List[Dict[str, str]], update_callback: Callable[[], Any] = None) -> AsyncGenerator[str, None]:
        """
        Получает потоковое завершение от языковой модели.

        Args:
            messages (List[Dict[str, str]]): Список сообщений для отправки модели.
            update_callback (Callable[[], Any], optional): Функция обратного вызова для обновления статуса.

        Yields:
            str: Части ответа от языковой модели.
        """
        pass