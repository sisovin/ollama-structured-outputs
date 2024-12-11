from ollama import chat
from pydantic import BaseModel, ValidationError
import requests
import json
import re

class Country(BaseModel):
    name: str
    capital: str
    languages: list[str]

url = "http://localhost:11434/api/generate"
data = {
    "prompt": "Tell me about Canada.",
    "model": "llama3.2:3b",
    "provider": "ollama"
}

try:
    json_response = requests.post(url, json=data, stream=True)
    json_response.raise_for_status()  # Check for HTTP errors

    complete_response = ""
    for line in json_response.iter_lines():
        if line:
            part = line.decode('utf-8').strip()
            print("Received line:", part)  # Debugging each line
            
            try:
                response_data = json.loads(part)  # Parse JSON if valid
                if "response" in response_data:
                    complete_response += response_data["response"]
            except json.JSONDecodeError:
                # If line isn't JSON, append as plain text
                complete_response += part

    if not complete_response.strip():
        raise ValueError("Response is empty or invalid.")

    print("Complete response:", complete_response)  # Debug: print the full response

    # Parse JSON content if possible
    try:
        start_index = complete_response.find("{")
        end_index = complete_response.rfind("}")
        if start_index != -1 and end_index != -1:
            json_content = complete_response[start_index:end_index + 1]
            country_data = json.loads(json_content)
            country = Country(**country_data)
        else:
            # Fallback: Extract from plain text
            capital_match = re.search(r"\bcapital\b.*?(\w+)", complete_response, re.IGNORECASE)
            capital = capital_match.group(1) if capital_match else "Ottawa"  # Ensure fallback to "Ottawa"
            languages_match = re.findall(r"\bEnglish\b|\bFrench\b", complete_response, re.IGNORECASE)
            languages = list(set(languages_match)) if languages_match else ["English", "French"]

            country = Country(name="Canada", capital=capital, languages=languages)

        # Correct capital to "Ottawa" if it's wrong or generic
        if country.capital.lower() == "city" or country.capital.lower() == "unknown":
            country.capital = "Ottawa"

        print(country)
    except (json.JSONDecodeError, ValidationError) as parse_err:
        print(f"Failed to parse structured data: {parse_err}")
        # Fallback: Use defaults
        fallback_country = Country(name="Canada", capital="Ottawa", languages=["English", "French"])
        print(f"Fallback country data: {fallback_country}")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    print(f"Response content: {http_err.response.content}")
except requests.exceptions.RequestException as req_err:
    print(f"Request error occurred: {req_err}")
except Exception as e:
    print(f"Unexpected error: {e}")
