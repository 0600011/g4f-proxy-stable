# g4f-proxy-stable

**安定した g4f モデルのみ**を利用し、**OpenAI 互換 API** を提供する完全無料・無制限のローカルサーバーです。  
Python または Docker で簡単に実行できます。

---

## 特徴

* ✅ [g4f (gpt4free)](https://github.com/xtekky/gpt4free) の安定モデルのみ使用  
* ✅ [g4f-working](https://raw.githubusercontent.com/maruf009sultan/g4f-working/refs/heads/main/working/working_results.txt) から常に最新の利用可能モデルを取得  
* ✅ OpenAI 互換エンドポイント提供 (`/v1/models`, `/v1/chat/completions`)  
* ✅ 既存の OpenAI クライアント/ライブラリと互換 (`openai`, `requests` など)  
* ✅ Python または Docker でローカル実行可能  
* ✅ **完全無料 & 無制限** 🚀  

---

## Python で実行する

```bash
git clone https://github.com/unlimitedai2025-byte/g4f-proxy-stable.git
cd g4f-proxy-stable
pip install -r requirements.txt
python apiserver.py
````

デフォルトで **[http://127.0.0.1:8001](http://127.0.0.1:8001)** で起動します。

---

## Docker で実行する

```bash
docker pull 060001a/g4f-stable:latest
docker run -p 8001:8001 060001a/g4f-stable:latest
```

API は **[http://127.0.0.1:8001](http://127.0.0.1:8001)** で利用可能です。

---

## 使用例

### Python の `requests` を使用

```python
import requests

resp = requests.post(
    "http://127.0.0.1:8001/v1/chat/completions",
    json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "こんにちは！"}]
    }
)

print(resp.json()["choices"][0]["message"]["content"])
```

### OpenAI クライアントを使用

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8001/v1", api_key="not-needed")

chat = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "こんにちは！"}]
)

print(chat.choices[0].message.content)
```

---

## API エンドポイント

* `GET /v1/models` → 利用可能なモデル一覧
* `POST /v1/chat/completions` → Chat Completion (OpenAI互換、ストリーミング対応)

---

## 環境変数

* `PORT` (デフォルト: `8001`)

---

## 参考

* [g4f (gpt4free)](https://github.com/xtekky/gpt4free)
* [g4f-working](https://github.com/maruf009sultan/g4f-working)

---
