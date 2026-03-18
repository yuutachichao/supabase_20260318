# Supabase + Ollama 知識庫 API

一個簡單的 API，使用本地 Ollama 生成向量，存儲到 Supabase 資料庫。

## 功能

- 新增文章（自動生成向量）
- 刪除文章
- 向量搜尋

## 架構

```
Client → API (Zeabur) → Ollama (Zeabur) → Supabase (雲端)
```

## 環境變數

複製 `.env.example` 為 `.env` 並填入：

```bash
# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Ollama 配置
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=nomic-embed-text
```

## 本地測試

```bash
docker compose up -d
```

## API 使用

### 新增文章

```bash
curl -X POST http://localhost:8080/ingest/article \
  -H "Content-Type: application/json" \
  -d '{
    "title": "測試文章",
    "raw_content": "這是文章內容",
    "summary": "摘要",
    "tags": ["tag1", "tag2"]
  }'
```

### 搜尋文章

```bash
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "搜尋關鍵詞",
    "top_k": 3
  }'
```

### 刪除文章

```bash
curl -X DELETE http://localhost:8080/article/{article_id}
```

## 部署到 Zeabur

1. 將此專案推送到 GitHub
2. 在 Zeabur 選擇此 repo
3. 設定環境變數
4. 部署

## Supabase SQL

```sql
-- 啟用 pgvector 擴展
CREATE EXTENSION IF NOT EXISTS vector;

-- 建立 articles 資料表
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source_url TEXT,
    source_type TEXT DEFAULT 'web',
    language TEXT DEFAULT 'zh-TW',
    raw_content TEXT,
    summary TEXT,
    key_points JSONB,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    embedding vector(768)
);

-- 啟用 RLS
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- 允許讀取
CREATE POLICY "Allow public read" ON articles FOR SELECT USING (true);
-- 允許新增
CREATE POLICY "Allow public insert" ON articles FOR INSERT WITH CHECK (true);
-- 允許刪除
CREATE POLICY "Allow public delete" ON articles FOR DELETE USING (true);

-- 建立向量索引
CREATE INDEX ON articles USING ivfflat (embedding vector_cosine_ops);
```

## License

MIT
