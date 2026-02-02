from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"
TIMEOUT_SECONDS = 120

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    days: int = Field(..., ge=1, le=30)
    model: str | None = None


@app.get("/health")
def health():
    return {"ok": True}


def extract_json_substring(text: str):
    if not text:
        return None
    first_obj = text.find("{")
    first_arr = text.find("[")

    if first_obj == -1 and first_arr == -1:
        return None

    if first_obj == -1:
        start = first_arr
        end = text.rfind("]")
    elif first_arr == -1:
        start = first_obj
        end = text.rfind("}")
    else:
        start = min(first_obj, first_arr)
        if start == first_obj:
            end = text.rfind("}")
        else:
            end = text.rfind("]")

    if end == -1 or end <= start:
        return None
    return text[start : end + 1]


def call_ollama_json(model: str, prompt: str):
    payload = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.3},
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return {
            "ok": False,
            "error": f"Ollama 请求失败: {exc}",
            "raw": "",
            "debug": {"url": OLLAMA_URL, "model": model},
        }

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error": "Ollama 返回非 JSON",
            "raw": resp.text,
            "debug": {"url": OLLAMA_URL, "model": model},
        }

    raw = data.get("response", "")
    if not isinstance(raw, str):
        raw = str(raw)

    try:
        parsed = json.loads(raw)
        return {"ok": True, "data": parsed}
    except json.JSONDecodeError:
        trimmed = extract_json_substring(raw)
        if trimmed:
            try:
                parsed = json.loads(trimmed)
                return {"ok": True, "data": parsed}
            except json.JSONDecodeError:
                pass

    return {
        "ok": False,
        "error": "模型输出无法解析为严格 JSON",
        "raw": raw,
        "debug": {"url": OLLAMA_URL, "model": model, "ollama_keys": list(data.keys())},
    }


def build_prompt(topic: str, days: int):
    return (
        "你是一个资深工程导师。请严格只输出 JSON，不要任何多余文字或 markdown。\n"
        "输出 JSON 格式必须是：\n"
        "{\n"
        "  \"topic\": \"<topic>\",\n"
        "  \"days\": [\n"
        "    {\"day\": 1, \"title\": \"...\", \"tasks\": [\"...\",\"...\"]},\n"
        "    ...\n"
        "  ]\n"
        "}\n"
        "要求：day 从 1 到 days；title 简短；tasks 每天 2~4 条；中文输出；语气工程向（偏实操）。\n"
        f"topic={topic}\n"
        f"days={days}\n"
        "再次强调：只输出 JSON。"
    )


@app.post("/api/plan")
def api_plan(req: PlanRequest):
    model = (req.model or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    prompt = build_prompt(req.topic.strip(), req.days)

    result = call_ollama_json(model, prompt)
    if result.get("ok"):
        return {"ok": True, "data": result.get("data")}

    return {
        "ok": False,
        "error": result.get("error", "未知错误"),
        "raw": result.get("raw", ""),
        "debug": result.get("debug", {}),
    }
