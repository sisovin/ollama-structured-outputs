from ollama import chat
from pydantic import BaseModel
import requests
import json  # Import the json module
import re

class Country(BaseModel):
    name: str
    capital: str
    languages: list[str]

url = "http://localhost:11434/api/generate"  # Use localhost instead of 127.0.0.1
data = {
    "prompt": "Tell me about Canada.",
    "model": "llama3.2:3b",
    "provider": "ollama",
    "country": {
        "name": "str",
        "capital": "str",
        "languages": ["str"]
    }
}

try:
    json_response = requests.post(url, json=data, stream=True)
    json_response.raise_for_status()  # Check for HTTP errors
    
    complete_response = ""
    for line in json_response.iter_lines():
        if line:
            part = line.decode('utf-8')
            response_data = json.loads(part)  # Use the json module to parse JSON
            # print("Response part:", response_data)  # Print each part for debugging
            complete_response += response_data.get("response", "")
    
    print("Complete response:", complete_response)  # Print the complete response
    
    # Extracting information from the complete response
    name = "Canada"  # Since the prompt is about Canada, we can assume the name
    capital_match = re.search(r"\bcapital\b.*?(\w+)", complete_response, re.IGNORECASE)
    capital = capital_match.group(1) if capital_match else "Unknown"
    
    languages_match = re.search(r"\blanguages\b.*?(\w+)", complete_response, re.IGNORECASE)
    languages = ["English", "French"]  # Assuming these are the languages based on the response
    
    country_data = {
        "name": name,
        "capital": capital,
        "languages": languages
    }
    country = Country(**country_data)
    print(country)
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    print(f"Response content: {http_err.response.content}")
except requests.exceptions.RequestException as req_err:
    print(f"Request error occurred: {req_err}")
except ValueError as val_err:
    print(f"Value error occurred: {val_err}")
    # Fallback mechanism
    fallback_country = Country(name="Canada", capital="Ottawa", languages=["English", "French"])
    print(f"Fallback country data: {fallback_country}")
except Exception as e:
    print(e)