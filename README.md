# Project Title: Ollama JSON Stuctured Outputs

## Overview

This project demonstrates how to use the Ollama API to generate structured outputs using a JSON schema. The Ollama Python library supports structured outputs, making it possible to constrain a model’s output to a specific format defined by a JSON schema. This ensures more reliability and consistency in the responses.

### Use Cases for Structured Outputs

- Parsing data from documents
- Extracting data from images
- Structuring all language model responses
- More reliability and consistency than JSON mode

## Requirements

- Python 3.7+
- 

requests

 library
- 

pydantic

 library

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-repo/ollama-structured-outputs.git
    cd ollama-structured-outputs
    ```

2. Install the required libraries:
    ```sh
    pip install requests pydantic
    ```

## Usage

The 

test.py

 script demonstrates how to use the Ollama API to generate structured outputs. The script sends a request to the Ollama API with a prompt and a JSON schema, and then processes the response to extract structured data.

### Code Explanation

```python
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
```

### Explanation

1. **Define the 

Country

 Model**:
    - The 

Country

 class is defined using 

pydantic.BaseModel

 to represent the structured output.

2. **Define the JSON Schema**:
    - The 

json_schema

 dictionary defines the structure of the expected output, specifying the required properties: 

name

, 

capital

, and 

languages

.

3. **Send the Request**:
    - The script sends a POST request to the Ollama API with the prompt and the JSON schema. The 

stream=True

 parameter is used to handle streaming responses.

4. **Process the Response**:
    - The script processes the streaming response line by line, concatenating the 

response

 parts to form the complete response.

5. **Parse the Structured Output**:
    - The complete response is parsed according to the JSON schema to create a 

Country

 object. If parsing fails, a fallback mechanism provides default country information.

### Running the Script

To run the script, execute the following command:

```sh
python test.py
```

This will send a request to the Ollama API and print the structured output based on the JSON schema.

## Conclusion

This project demonstrates how to use the Ollama API to generate structured outputs using a JSON schema. By defining a schema, you can ensure more reliability and consistency in the responses, making it suitable for various use cases such as parsing data from documents, extracting data from images, and structuring all language model responses.