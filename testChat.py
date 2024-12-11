import logging
import json
import httpx
from pydantic import BaseModel, ValidationError

OLLAMA_SERVER_URL = "http://localhost:11434"

class Country(BaseModel):
    name: str
    capital: str
    languages: list[str]

logging.basicConfig(level=logging.DEBUG)

data = {
    "model": "llama3.2:3b",
    "messages": [{"role": "user", "content": "Tell me about Canada."}],
    "format": Country.model_json_schema(),
}

try:
    # Increase timeout to 60 seconds
    with httpx.Client(base_url=OLLAMA_SERVER_URL, timeout=None) as client:
        with client.stream("POST", "/api/chat", json=data) as response:
            if response.status_code == 200:
                complete_response = ""
                for line in response.iter_lines():
                    if line:
                        # Parse each JSON line
                        json_line = json.loads(line)
                        if "message" in json_line and "content" in json_line["message"]:
                            complete_response += json_line["message"]["content"]
                        if json_line.get("done", False):
                            break  # End of the stream

                print("Complete response:", complete_response)

                try:
                    country = Country.model_validate_json(complete_response)
                    print("Output:", country)
                except ValidationError as parse_err:
                    print("Validation error:", parse_err)
                    print("Raw Content:", complete_response)
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                
except Exception as e:
    print(f"Unexpected error: {e}")
