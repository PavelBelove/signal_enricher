import os
import sys
import signal
import openai
from config.api_keys import api_keys

# Set the OpenAI API key
openai.api_key = api_keys["openai_api_key"]

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

def gpt_query(messages):
    """
    Query the GPT-4o model with a list of messages.

    Args:
        messages (list): List of messages to send to the GPT-4 model.

    Returns:
        tuple: A tuple containing the response content and the number of tokens used.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=100,
        temperature=0.3
    )
    content = response.choices[0].message['content']
    tokens_used = response['usage']['total_tokens']
    return content, tokens_used