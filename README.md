# Ollama FastAPI Starter

一个最小可运行的本地 LLM 全栈模板：浏览器调用 FastAPI，FastAPI 调用本机 Ollama，并将严格 JSON 结果渲染为学习计划卡片。

## 功能

- FastAPI 健康检查和计划生成接口
- Ollama JSON 模式及异常兜底解析
- 可配置模型、超时、Ollama 地址和 CORS 来源
- 无构建步骤的静态前端
- 单元测试与 GitHub Actions

## 目录结构

```text
backend/             FastAPI 服务
frontend/            静态网页
tests/               单元测试
.env.example         环境变量示例
requirements-dev.txt 开发与 CI 依赖入口
```

## 快速开始

先安装并启动 [Ollama](https://ollama.com/)，然后拉取默认模型：

```powershell
ollama pull qwen2.5:7b
```

启动后端：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

另开一个终端启动前端：

```powershell
python -m http.server 5173 --directory frontend
```

访问 `http://127.0.0.1:5173/`。健康检查地址为 `http://127.0.0.1:8000/health`。

macOS 或 Linux 只需把虚拟环境激活命令改为 `source .venv/bin/activate`。

## 配置

复制 `.env.example` 后，可通过系统环境变量覆盖以下配置：

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama API 地址 |
| `OLLAMA_MODEL` | `qwen2.5:7b` | 默认模型 |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | 请求超时秒数 |
| `CORS_ORIGINS` | 本地 5173 端口 | 逗号分隔的前端来源 |

应用不会自动读取 `.env` 文件；可在 PowerShell 中使用 `$env:变量名="值"`，或由部署平台注入环境变量。

## 接口

- `GET /health`
- `POST /api/plan`

请求示例：

```json
{
  "topic": "学习大模型",
  "days": 7,
  "model": "qwen2.5:7b"
}
```

## 本地检查

```powershell
python -m pip install -r requirements-dev.txt
python -m compileall -q backend
python -m unittest discover -s tests -v
```
