# IBM WatsonX AI Foundational Server

## Introduction
For the duration of the enterprise RAG challenge, we have our own server for interacting with IBM Foundation Models!

Important! It is private. Don’t share access keys with the others. Contact Rinat Abdullin (TimeToAct Austria) on Teams or discord, if you are interested in building RAG solution for the Enterprise RAG Challenge on top of WatsonX AI.

Server is rate-limited, and total usage is capped, to avoid accidentally overloading upstream servers. You can use balance endpoint to keep an eye on your usage.

It is OK to exceed it, if you have an explanation. Just talk to Rinat, if you need more.

How to use the server? Just send a HTTP JSON request in a common format, passing your own key. We have curl samples below, but if you want to have an client in a library of your choice, just:

- Copy-paste this page to Claude/ChatGPT/etc
- Ask to write a method for prompting models in a language of your choice.

 
### How to get the IBM API key?

Just write Rinat Abdullin a short message on Teams/discord along these lines:

```
Hi, I want to use IBM WatsonX AI models to participate in the Enterprise RAG Challenge! 
I’m planning to use models (list models you are planning to use) and will try these approaches/frameworks: 
(list how you plan to approach the challenge).
```

This is just a formality to ensure that the approach is a sensible one and we don’t plan to accidentally overload IBM servers.



## API Endpoints

### Get Balance

Returns the current balance for the provided token.

Bash:
```bash
curl https://rag.timetoact.at/ibm/balance \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Python:
```python
import requests 
balance_url = "https://rag.timetoact.at/ibm/balance"
balance_headers = {"Authorization": f"Bearer {YOUR_TOKEN}"}

try:
    balance_response = requests.get(balance_url, headers=balance_headers)
    balance_response.raise_for_status()
    print("Balance Response:", balance_response.json())
except requests.HTTPError as err:
    print(err)
```


### Get Available Models

```bash
curl https://rag.timetoact.at/ibm/foundation_model_specs
```

Provided foundation model details [here](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-details.html?context=wx).


### Get Embeddings

Returns vector embeddings for the provided text inputs. Each input string will be converted into a vector of floating point numbers that represents its semantic meaning.

Bash:
```bash
curl -X POST https://rag.timetoact.at/ibm/embeddings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      "Youth craves thrills while adulthood cherishes wisdom.",
      "Youth seeks ambition while adulthood finds contentment.",
      "Dreams chased in youth while goals pursued in adulthood."
    ],
    "model_id": "ibm/granite-embedding-107m-multilingual"
  }'
```

Python:
```python
import requests 

url = "https://rag.timetoact.at/ibm/embeddings"
headers = {
    "Authorization": f"Bearer {YOUR_TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "inputs": [
        "Youth craves thrills while adulthood cherishes wisdom.",
        "Youth seeks ambition while adulthood finds contentment.",
        "Dreams chased in youth while goals pursued in adulthood."
    ],
    "model_id": "ibm/granite-embedding-107m-multilingual"
}

try:
    embedding_response = requests.post(url, headers=headers, json=payload)
    embedding_response.raise_for_status()
    print("Embeddings Response:", embedding_response.json())
except requests.HTTPError as err:
    print(err)
```




### Generate Text

Bash:
```bash
curl -X POST https://rag.timetoact.at/ibm/text_generation \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ],
    "model_id": "ibm/granite-34b-code-instruct",
    "parameters": {
      "max_new_tokens": 100,
      "min_new_tokens": 1
    }
  }'
```

Python:
```python
import requests 

text_generation_url = "https://rag.timetoact.at/ibm/text_generation"
text_generation_headers = {
    "Authorization": f"Bearer {YOUR_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "input": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the date today?"}
    ],
    "model_id": "ibm/granite-34b-code-instruct",
    "parameters": {
        "max_new_tokens": 100,
        "min_new_tokens": 1
    }
}

try:
    text_response = requests.post(text_generation_url, headers=text_generation_headers, json=payload)
    text_response.raise_for_status()
    print("Text Generation Response:", text_response.json())
except requests.HTTPError as err:
    print(err)
```

### Available Parameters

https://ibm.github.io/watson-machine-learning-sdk/model.html

All parameters are optional with reasonable defaults.

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| decoding_method | string | Either "greedy" or "sample" | "greedy" |
| temperature | float | Controls randomness (0.0-1.0) | 0.0 |
| top_p | float | Nucleus sampling parameter | 1.0 |
| top_k | integer | Top-k sampling parameter | 0 |
| repetition_penalty | float | Penalizes repeated tokens | 1.0 |
| random_seed | integer | Seed for reproducible results | 0 |
| min_new_tokens | integer | Minimum tokens to generate | 0 |
| max_new_tokens | integer | Maximum tokens to generate | 100 |
| time_limit | integer | Maximum generation time in seconds | 0 |


### Example with All Parameters

```bash
curl -X POST http://localhost:8080/text_generation \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Tell me a short story about a cat."}
    ],
    "model_id": "ibm/granite-34b-code-instruct",
    "parameters": {
      "decoding_method": "sample",
      "temperature": 0.7,
      "top_p": 0.9,
      "top_k": 50,
      "repetition_penalty": 1.2,
      "random_seed": 42,
      "min_new_tokens": 10,
      "max_new_tokens": 200,
      "time_limit": 30
    }
  }'
```

## Model Prices

Each request is charged for both input and output tokens.

Price list of IBM models [here](https://www.ibm.com/de-de/products/watsonx-ai/pricing)

Provided foundation model details [here](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-details.html?context=wx).

### Embedding Model Prices per 1'000'000 Tokens ($)
(Not all included via our server, check available models with code above)

| Model | Price per 1M tokens |
|-------|-------------------|
| sentence-transformers/all-minilm-l6-v2 | 0.10 |
| sentence-transformers/all-minilm-l12-v2 | 0.10 |
| ibm/granite-embedding-107m-multilingual | 0.10 |
| ibm/granite-embedding-278m-multilingual | 0.10 |
| ibm/slate-30m-english-rtrvr-v2 | 0.10 |
| ibm/slate-30m-english-rtrvr | 0.10 |
| ibm/slate-125m-english-rtrvr-v2 | 0.10 |
| ibm/slate-125m-english-rtrvr | 0.10 |

### Language Model Prices per 1'000'000 Tokens ($)

| Model | Input (1M tokens) | Output (1M tokens) |
|--------|-------------------|--------------------|
| codellama/codellama-34b-instruct-hf | 1.80              | 1.80               |
| google/flan-t5-xl | 0.60              | 0.60               |
| google/flan-t5-xxl | 1.80              | 1.80               |
| google/flan-ul2 | 5.00              | 5.00               |
| ibm/granite-13b-instruct-v2 | 0.60              | 0.60               |
| ibm/granite-20b-code-instruct | 0.60              | 0.60               |
| ibm/granite-20b-multilingual | 0.60              | 0.60               |
| ibm/granite-3-2b-instruct | 0.10              | 0.10               |
| ibm/granite-3-8b-instruct | 0.20              | 0.20               |
| ibm/granite-34b-code-instruct | 0.60              | 0.60               |
| ibm/granite-3b-code-instruct | 0.60              | 0.60               |
| ibm/granite-8b-code-instruct | 0.60              | 0.60               |
| ibm/granite-guardian-3-2b | 0.10              | 0.10               |
| ibm/granite-guardian-3-8b | 0.20              | 0.20               |
| meta-llama/llama-2-13b-chat | 5.22              | 5.22               |
| meta-llama/llama-3-1-70b-instruct | 1.80              | 1.80               |
| meta-llama/llama-3-1-8b-instruct | 0.60              | 0.60               |
| meta-llama/llama-3-2-11b-vision-instruct | 0.35              | 0.35               |
| meta-llama/llama-3-2-1b-instruct | 0.10              | 0.10               |
| meta-llama/llama-3-2-3b-instruct | 0.15              | 0.15               |
| meta-llama/llama-3-2-90b-vision-instruct | 2.00              | 2.00               |
| meta-llama/llama-3-3-70b-instruct | 1.80              | 1.80               |
| meta-llama/llama-guard-3-11b-vision | 0.35              | 0.35               |
| meta-llama/llama-3-405b-instruct | 5.00              | 16.00              |
| mistralai/mistral-large | 3.00              | 10.00              |
| mistralai/mixtral-8x7b-instruct-v01 | 0.60              | 0.60               |
| deepseek/deepseek-r1-distill-llama-70b | 1.00              | 1.00               |



