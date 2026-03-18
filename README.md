# Supabase + OpenClaw 知識庫

一個使用 Jina AI 生成向量，存儲到 Supabase 的知識庫 API。

## 功能

- ✅ 新增文章（自動生成向量）
- ✅ 刪除文章
- ✅ 向量搜尋
- ✅ 文字搜尋（備用）

## 架構

```
OpenClaw → API (Zeabur) → Jina AI → Supabase (雲端)
```

## 快速開始

### 1. Supabase 設定

參考 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

### 2. 環境變數

在 Zeabur 上設定：

| 變數 | 說明 |
|------|------|
| `SUPABASE_URL` | Supabase 專案網址 |
| `SUPABASE_KEY` | anon public key |
| `JINA_API_KEY` | Jina AI API Key |
| `USE_VECTOR` | true |

### 3. 部署

```bash
docker compose up -d
```

## API 文件

- 健康檢查：`GET /health`
- 新增文章：`POST /ingest/article`
- 搜尋文章：`POST /search`
- 刪除文章：`DELETE /article/{id}`

詳細說明見 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## License

MIT
