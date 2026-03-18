# Supabase + Ollama Zeabur 部署说明

## 架构

在 Zeabur 上需要部署两个服务：
1. **Ollama** - 向量生成服务
2. **API** - 你的知识库 API

---

## 步骤 1: 部署 Ollama

1. 在 Zeabur 创建新服务
2. 选择 **Ollama** (如果有) 或者用 Docker:
   - 镜像: `ollama/ollama:latest`
   - 端口: `11434`
3. 环境变量: 不需要
4. 获取 Ollama 的 URL

---

## 步骤 2: 部署 API

1. 部署这个项目
2. 设置环境变量:

| 变量 | 值 |
|------|-----|
| SUPABASE_URL | `https://rjxyvqmhskusodofvivc.supabase.co` |
| SUPABASE_KEY | `eyJhbGci...` |
| OLLAMA_BASE_URL | `http://你的Ollama服务.zeabur.app:11434` |
| OLLAMA_MODEL | `nomic-embed-text` |
| USE_VECTOR | `true` |

---

## 简化方案

如果 Zeabur 不方便跑 Ollama，可以考虑：
1. **用 OpenAI API**（需要充值）
2. **本地跑 Ollama + ngrok**（免费但需要本机一直开着）
3. **用免费的嵌入 API**（如 HuggingFace）

你想怎么处理？
