# tests/test_utils.py

import pytest
import os
import signal
import sys
from unittest.mock import MagicMock, patch
from modules.utils import load_role_description, signal_handler, gpt_query

def test_load_role_description(tmp_path):
    role_description = "This is a test role description."
    file_path = tmp_path / "role_description.txt"
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(role_description)

    loaded_description = load_role_description(file_path)
    assert loaded_description == role_description

def test_signal_handler():
    workbook = MagicMock()
    filename = "test.xlsx"
    with patch('sys.exit') as mock_exit:
        signal_handler(signal.SIGINT, None, workbook, filename, verbose=True)
        workbook.save.assert_called_once_with(filename)
        workbook.close.assert_called_once()
        mock_exit.assert_called_once_with(0)

@patch('openai.ChatCompletion.create')
def test_gpt_query(mock_create):
    mock_response = MagicMock()
    mock_response.choices[0].message = {'content': 'Test response'}
    mock_response.usage = {'total_tokens': 42}
    mock_create.return_value = mock_response

    messages = [{"role": "user", "content": "Hello, GPT-4"}]
    content, tokens_used = gpt_query(messages)

    assert content == 'Test response'
    assert tokens_used == 42
    mock_create.assert_called_once_with(
        model="gpt-4",
        messages=messages,
        max_tokens=100,
        temperature=0.7
    )