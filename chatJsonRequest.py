import json
import logging
from pydantic import BaseModel, ValidationError
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Define the Ollama server URL
OLLAMA_SERVER_URL = os.getenv("OLLAMA_SERVER_URL", "http://127.0.0.1:11434")
print(f"OLLAMA_SERVER_URL: {OLLAMA_SERVER_URL}")

# Define the Country model
class Country(BaseModel):
    name: str
    capital: str
    languages: list[str]

# Load the request data from request.json
with open("request.json", "r") as file:
    request_data = json.load(file)

try:
    # Send the POST request to Ollama server
    with httpx.Client(base_url=OLLAMA_SERVER_URL, timeout=None) as client:
        response = client.post("/api/chat", json=request_data)

        # Check if the response was successful
        if response.status_code == 200:
            response_data = response.json()

            # Extract the message content
            if "message" in response_data and "content" in response_data["message"]:
                raw_content = response_data["message"]["content"]

                try:
                    # Parse the content using the Country model
                    country = Country.model_validate_json(raw_content)
                    print("Output:", country)
                except ValidationError as parse_err:
                    print("Validation Error:", parse_err)
                    print("Raw Content:", raw_content)
            else:
                print("Unexpected response format:", response_data)
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response Text: {response.text}")

except httpx.RequestError as e:
    print(f"Request error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
