---

# g4f-proxy-stable

A completely free & unlimited local server that uses only **stable g4f models** and provides an **OpenAI-compatible API**.
Run it directly with Python or via Docker.

---

## Features

* ✅ Uses only **stable** models from [g4f (gpt4free)](https://github.com/xtekky/gpt4free)
* ✅ Provides **OpenAI-compatible endpoints** (`/v1/models`, `/v1/chat/completions`)
* ✅ Works with existing OpenAI clients/libraries (`openai`, `requests`, etc.)
* ✅ Run locally with **Python** or **Docker**
* ✅ **Completely free & unlimited** 🚀

---

## Run with Python

### 1. Clone the repo

git clone [https://github.com/yourname/g4f-proxy-stable.git](https://github.com/yourname/g4f-proxy-stable.git)
cd g4f-proxy-stable

### 2. Install dependencies

pip install -r requirements.txt

### 3. Start the server

python apiserver.py

By default, it runs on **[http://127.0.0.1:8001](http://127.0.0.1:8001)**

---

## Run with Docker

### Pull image from Docker Hub

docker pull 060001a/g4f-stable\:latest

### Run the container

docker run -p 8001:8001 060001a/g4f-stable\:latest

The API will be available at **[http://127.0.0.1:8001](http://127.0.0.1:8001)**

---

## Example Usage

### Using `requests` (Python)

import requests

resp = requests.post(
"[http://127.0.0.1:8001/v1/chat/completions](http://127.0.0.1:8001/v1/chat/completions)",
json={
"model": "gpt-3.5-turbo",
"messages": \[{"role": "user", "content": "Hello!"}]
}
)

print(resp.json()\["choices"]\[0]\["message"]\["content"])

### Using OpenAI client

from openai import OpenAI

client = OpenAI(base\_url="[http://127.0.0.1:8001/v1](http://127.0.0.1:8001/v1)", api\_key="not-needed")

chat = client.chat.completions.create(
model="gpt-3.5-turbo",
messages=\[{"role": "user", "content": "Hello from g4f-proxy-stable!"}]
)

print(chat.choices\[0].message.content)

---

## API Endpoints

* `GET /v1/models` → List available models
* `POST /v1/chat/completions` → Chat completion (OpenAI-compatible, supports streaming)

---

## Environment Variables

* `PORT` (default: `8001`)

---

## References

* [g4f (gpt4free)](https://github.com/xtekky/gpt4free)
* [g4f-working](https://github.com/maruf009sultan/g4f-working)

---

👉 これをそのまま README に貼れば完成です！
