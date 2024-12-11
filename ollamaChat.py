import logging
from pydantic import BaseModel, ValidationError
import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Define the Ollama server URL
OLLAMA_SERVER_URL = os.getenv("OLLAMA_SERVER_URL", "http://localhost:11434")
print(f"OLLAMA_SERVER_URL: {OLLAMA_SERVER_URL}")

# Define the Country model
class Country(BaseModel):
    name: str
    capital: str
    languages: list[str]

# Prepare payload
payload = {
    "model": "llama3.2:3b",
    "messages": [
        {"role": "user", "content": "Tell me about Canada."}
    ],
    "format": Country.model_json_schema(),
}

try:
    # Send the request and handle streaming
    with httpx.Client(base_url=OLLAMA_SERVER_URL, timeout=None) as client:
        with client.stream("POST", "/api/chat", json=payload) as response:
            if response.status_code == 200:
                full_content = ""
                for line in response.iter_lines():
                    if line:
                        # Parse each JSON line
                        json_line = json.loads(line)
                        if "message" in json_line and "content" in json_line["message"]:
                            full_content += json_line["message"]["content"]
                        if json_line.get("done", False):
                            break  # End of the stream
                
                print("Full Response Content:", full_content)

                # Parse the full content into the Country model if applicable
                try:
                    country = Country.model_validate_json(full_content)
                    print("Parsed Country Data:", country)
                except ValidationError as parse_err:
                    print("Validation error:", parse_err)
                    print("Raw Content:", full_content)
            else:
                print(f"Error: Received status code {response.status_code}")

except httpx.RequestError as e:
    print(f"Request error: {e}")
