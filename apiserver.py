import sys, subprocess, importlib

required_packages = ["fastapi", "uvicorn", "requests", "g4f"]

for pkg in required_packages:
    try:
        importlib.import_module(pkg)
    except ImportError:
        print(f"[INFO] インストール中: {pkg}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {pkg} のインストールに失敗しました: {e}")
            print("`pip install fastapi uvicorn requests g4f` を実行して下さい。")
            sys.exit(1)

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import json, random, requests, g4f, uvicorn

TXT_URL = "https://raw.githubusercontent.com/maruf009sultan/g4f-working/refs/heads/main/working/working_results.txt"

app = FastAPI()

# モデル取得
def loadModels():
    try:
        lines = requests.get(TXT_URL).text.strip().splitlines()
    except:
        return {}, []
    mMap = {}
    mList = []
    for l in lines:
        if "|" not in l:
            continue
        prov, model, typ = l.split("|")
        if typ != "text" or "flux" in model.lower():
            continue
        if model not in mMap:
            mMap[model] = []
        mMap[model].append(prov)
        if not any(x["id"] == model for x in mList):
            mList.append({
                "id": model,
                "object": "model",
                "created": 0,
                "owned_by": "multiple" if len(mMap[model]) > 1 else prov,
                "permission": []
            })
    return mMap, mList

# プロバイダー取得
def getProv(name):
    try:
        return getattr(g4f.Provider, name)
    except:
        return name

def grabText(chunk):
    try:
        if chunk is None:
            return ""
        if isinstance(chunk, str):
            return chunk
        if isinstance(chunk, (list, tuple)):
            return "".join(grabText(c) for c in chunk)
        if isinstance(chunk, dict):
            for k in ("text", "content", "message", "data"):
                if k in chunk and chunk[k]:
                    v = chunk[k]
                    if isinstance(v, dict):
                        return v.get("text") or v.get("content") or json.dumps(v, ensure_ascii=False)
                    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
            return json.dumps(chunk, ensure_ascii=False)
        for a in ("text", "content", "message", "data"):
            if hasattr(chunk, a):
                v = getattr(chunk, a)
                if v is None:
                    continue
                if isinstance(v, str):
                    return v
                if isinstance(v, (list, tuple)):
                    return "".join(grabText(x) for x in v)
                if isinstance(v, dict):
                    return v.get("text") or v.get("content") or json.dumps(v, ensure_ascii=False)
        return str(chunk)
    except:
        return str(chunk) if chunk is not None else ""

MODEL_MAP, MODELS_LIST = loadModels()

@app.get("/v1/models")
def models():
    return {"object": "list", "data": MODELS_LIST}

@app.post("/v1/chat/completions")
async def chatCompletions(req: Request):
    data = await req.json()
    model = data.get("model")
    messages = data.get("messages", [])
    isStream = data.get("stream", False)
    if model not in MODEL_MAP:
        return JSONResponse({"error": "no such model"}, status_code=404)
    prov = random.choice(MODEL_MAP[model])
    provObj = getProv(prov)
    extra = {}
    for k in ("temperature", "max_tokens", "stop", "stream"):
        if k in data:
            extra[k] = data[k]
    if isStream:
        def streamGen():
            try:
                res = g4f.ChatCompletion.create(model=model, provider=provObj, messages=messages, stream=True, **extra)
                count = 0
                for ch in res:
                    txt = grabText(ch)
                    if not txt:
                        continue
                    count += 1
                    yield "data: " + json.dumps({
                        "id": f"chatcmpl-{random.randint(1,9999999)}-{count}",
                        "object": "chat.completion.chunk",
                        "model": model,
                        "choices": [{"delta": {"content": txt}, "index": 0}]
                    }, ensure_ascii=False) + "\n\n"
                yield "data: " + json.dumps({
                    "id": f"chatcmpl-{random.randint(1,9999999)}-final",
                    "object": "chat.completion",
                    "model": model,
                    "choices": [{"delta": {}, "index": 0, "finish_reason": "stop"}]
                }, ensure_ascii=False) + "\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield "data: " + json.dumps({"error": str(e)}, ensure_ascii=False) + "\n\n"
        return StreamingResponse(streamGen(), media_type="text/event-stream", headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        })
    else:
        try:
            resp = g4f.ChatCompletion.create(model=model, provider=provObj, messages=messages, stream=False, **extra)
            txt = grabText(resp)
            return JSONResponse({
                "id": f"g4f-{random.randint(1, 9999999)}",
                "object": "chat.completion",
                "choices": [{
                    "message": {"role": "assistant", "content": txt},
                    "finish_reason": "stop",
                    "index": 0
                }]
            })
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import os
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", 8001)))