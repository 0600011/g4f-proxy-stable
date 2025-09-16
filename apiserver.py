import sys, subprocess, importlib
required_packages = ["fastapi", "uvicorn", "requests", "g4f"]
try:
    for pkg in required_packages:
        importlib.import_module(pkg)
except ImportError:
    print("[INFO] Installing dependencies from requirements.txt")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        sys.exit(1)
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import json, random, requests, g4f, uvicorn
TXT_URL = "https://raw.githubusercontent.com/maruf009sultan/g4f-working/refs/heads/main/working/working_results.txt"
app = FastAPI()
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
    import json
    # インデント付きでJSON整形（ソートせずにそのまま保持）
    import json
    from fastapi.responses import Response
    formatted = json.dumps({"object": "list", "data": MODELS_LIST}, ensure_ascii=False, indent=2)
    return Response(content=formatted, media_type="application/json; charset=utf-8")
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
        if k in data and k != "stream":
            extra[k] = data[k]
    if isStream:
        def streamGen():
            try:
                res = g4f.ChatCompletion.create(model=model, provider=provObj, messages=messages, stream=True, **extra)
                for ch in res:
                    txt = grabText(ch)
                    if txt is None:
                        txt = ""
                    yield "data: " + json.dumps({
                        "choices": [{"index": 0, "delta": {"role": "assistant", "content": txt}, "logprobs": None, "finish_reason": None}],
                        "id": f"chatcmpl-{random.randint(1,9999999)}",
                        "object": "chat.completion.chunk",
                        "created": int(random.randint(1_600_000_000, 1_900_000_000)),
                        "model": model,
                        "system_fingerprint": None
                    }, ensure_ascii=False) + "\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                import traceback, sys
                err_str = "".join(traceback.format_exception(*sys.exc_info()))
                print("[STREAM ERROR]", err_str)
                # ストリームモードのエラーもOpenAI SSE互換形式で返す
                yield "data: " + json.dumps({
                    "choices": [{
                        "index": 0,
                        "delta": {"role": "assistant", "content": f"[ERROR] {str(e)}"},
                        "logprobs": None,
                        "finish_reason": "error"
                    }],
                    "id": f"chatcmpl-{random.randint(1,9999999)}",
                    "object": "chat.completion.chunk",
                    "created": int(random.randint(1_600_000_000, 1_900_000_000)),
                    "model": model,
                    "system_fingerprint": None
                }, ensure_ascii=False) + "\n\n"
                yield "data: [DONE]\n\n"
        return StreamingResponse(streamGen(), media_type="text/event-stream", headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        })
    else:
        try:
            print("[DEBUG] Non-stream request received:", data)
            import asyncio
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            async def run_async():
                return await asyncio.to_thread(
                    g4f.ChatCompletion.create,
                    model=model, provider=provObj, messages=messages, stream=False, **extra
                )

            if loop and loop.is_running():
                print("[DEBUG] Running in existing event loop (concurrent safe mode)")
                resp = await run_async()
            else:
                print("[DEBUG] Starting new event loop for request")
                resp = asyncio.run(run_async())

            txt = grabText(resp)
            response_json = {
                "id": f"chatcmpl-{random.randint(1, 9999999)}",
                "object": "chat.completion",
                "created": int(random.randint(1_600_000_000, 1_900_000_000)),
                "model": model,
                "system_fingerprint": None,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": txt},
                    "logprobs": None,
                    "finish_reason": "stop"
                }]
            }
            print("[DEBUG] Non-stream response:", response_json)
            return response_json
        except Exception as e:
            import traceback, sys
            err_str = "".join(traceback.format_exception(*sys.exc_info()))
            print("[NON-STREAM ERROR]", err_str)
            error_json = {
                "id": f"chatcmpl-{random.randint(1, 9999999)}",
                "object": "chat.completion",
                "created": int(random.randint(1_600_000_000, 1_900_000_000)),
                "model": model,
                "system_fingerprint": None,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": f"[ERROR] {str(e)}"},
                    "logprobs": None,
                    "finish_reason": "error"
                }]
            }
            print("[DEBUG] Non-stream error response:", error_json)
            return error_json
if __name__ == "__main__":
    import os, sys
    host_bind = "0.0.0.0"
    uvicorn.run(
        app,
        host=host_bind,
        port=int(os.getenv("PORT", 8001)),
        timeout_keep_alive=30,
        log_level="debug",
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
