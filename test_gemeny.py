import google.generativeai as genai
from config.api_keys import api_keys
import json

# Load the configuration
with open('config/search_config.json', 'r') as f:
    config = json.load(f)

gemeni_api_key = api_keys["gemeni_api_key"]

# Configure Gemini API
genai.configure(api_key=gemeni_api_key)

def test_gemini_api():
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = "Analyze this short text: 'The quick brown fox jumps over the lazy dog.'"
    
    print("Sending request to Gemini API...")
    response = model.generate_content(prompt)
    print("Response received.")
    print("Content:", response.text)
    print("Prompt tokens:", len(prompt.split()))
    print("Response tokens:", len(response.text.split()))

if __name__ == "__main__":
    test_gemini_api()