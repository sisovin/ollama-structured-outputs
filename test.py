from pydantic import BaseModel
import requests
import json

class Country(BaseModel):
    name: str
    capital: str
    languages: list[str]

# Define the JSON schema for the expected output
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "capital": {"type": "string"},
        "languages": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["name", "capital", "languages"]
}

url = "http://localhost:11434/api/generate"  # Use localhost instead of 127.0.0.1
data = {
    "prompt": "Tell me about Canada.",
    "model": "llama3.2:3b",
    "provider": "ollama",
    "schema": json_schema  # Include the JSON schema in the request
}

try:
    json_response = requests.post(url, json=data, stream=True)
    json_response.raise_for_status()  # Check for HTTP errors
    
    complete_response = ""
    for line in json_response.iter_lines():
        if line:
            part = line.decode('utf-8')
            try:
                response_data = json.loads(part)  # Use the json module to parse JSON
                # print("Response part:", response_data)  # Print each part for debugging
                complete_response += response_data.get("response", "")
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {part}")
    
    print("Complete response:", complete_response)  # Print the complete response
    
    # Parse the structured output according to the JSON schema
    try:
        country_data = json.loads(complete_response)
        country = Country(**country_data)
        print(country)
    except json.JSONDecodeError as val_err:
        print(f"Value error occurred: {val_err}")
        # Fallback mechanism
        fallback_country = Country(name="Canada", capital="Ottawa", languages=["English", "French"])
        print(f"Fallback country data: {fallback_country}")
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    print(f"Response content: {http_err.response.content}")
except requests.exceptions.RequestException as req_err:
    print(f"Request error occurred: {req_err}")
except Exception as e:
    print(e)