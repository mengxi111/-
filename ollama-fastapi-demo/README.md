# Ollama + FastAPI 最小可运行模板

前端点击按钮调用 FastAPI，FastAPI 调用本机 Ollama，返回严格 JSON，并在前端渲染成卡片列表。

## 目录结构

```
ollama-fastapi-demo/
  backend/
    app.py
    requirements.txt
  frontend/
    index.html
  README.md
```

## 前置条件

- 安装并启动 Ollama
- 拉取模型：

```
ollama pull qwen2.5:7b
```

## 后端启动

### Windows PowerShell

```
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### macOS / Linux

```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

健康检查：

```
GET http://127.0.0.1:8000/health
```

## 前端启动

- 直接双击打开 `frontend/index.html`
- 或者用简单静态服务器：

```
cd frontend
python -m http.server 5173
```

然后访问：`http://127.0.0.1:5173/index.html`

## 常见问题

1) 连不上 11434
- 确认 Ollama 已启动并监听 11434 端口
- 在浏览器访问 `http://localhost:11434` 看是否有响应

2) 模型不输出 JSON
- 已在后端强制 `format="json"` 并做了兜底裁剪解析
- 如果仍失败，接口会返回 `ok=false`，前端会显示 `raw` 原文用于排查

## 接口说明

- `GET /health` -> `{ "ok": true }`
- `POST /api/plan`

请求体：

```
{
  "topic": "学习大模型",
  "days": 7,
  "model": "qwen2.5:7b"
}
```

成功响应：

```
{
  "ok": true,
  "data": {
    "topic": "学习大模型",
    "days": [
      {"day": 1, "title": "...", "tasks": ["...", "..."]}
    ]
  }
}
```

失败响应：

```
{
  "ok": false,
  "error": "...",
  "raw": "...",
  "debug": {"...": "..."}
}
```
