# Supabase + OpenClaw 部署完整指南

> 這是 2026-03-18 的部署記錄

## 系統架構

```
┌─────────────────┐      ┌──────────────────────┐      ┌────────────────┐
│   OpenClaw      │ ───▶ │  supabase-20260318  │ ───▶ │   Supabase     │
│   (Zeabur)     │      │  (Zeabur API)      │      │   (雲端數據庫)  │
│                 │      │  + Jina AI         │      │                │
└─────────────────┘      └──────────────────────┘      └────────────────┘
```

## 一、Supabase 雲端數據庫設定

### 1. 申請帳號
- 官網：https://supabase.com
- 用 GitHub 登入最簡單

### 2. 建立專案
- 名稱：`openclaw-knowledge`（或隨意）
- Region：選擇離台灣近的（Tokyo 或 Singapore）
- 密碼：記下來！

### 3. 取得 API Key
- Settings → API
- 取得 `Project URL` 和 `anon public key`

### 4. 建立資料表（SQL Editor）

```sql
-- 啟用 pgvector 擴展
CREATE EXTENSION IF NOT EXISTS vector;

-- 建立 articles 資料表
CREATE TABLE IF NOT EXISTS articles (
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
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 啟用 Row Level Security
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- 允許讀取/新增/刪除
CREATE POLICY "Allow public read" ON articles FOR SELECT USING (true);
CREATE POLICY "Allow public insert" ON articles FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public delete" ON articles FOR DELETE USING (true);

-- 建立向量欄位（768維，對應 Jina AI）
ALTER TABLE articles ADD COLUMN IF NOT EXISTS embedding vector(768);

-- 建立索引
CREATE INDEX IF NOT EXISTS articles_embedding_idx ON articles USING ivfflat (embedding vector_cosine_ops);
```

**重要：向量維度是 768（Jina AI），不是 1536（OpenAI）！**

---

## 二、Zeabur 部署 supabase-20260318

### 1. GitHub Repo
- https://github.com/yuutachichao/supabase-20260318

### 2. 部署步驟
1. Zeabur → New Project → Import from GitHub
2. 選擇 `yuutachichao/supabase-20260318`

### 3. 環境變數

| 變數 | 值 | 說明 |
|------|-----|------|
| `SUPABASE_URL` | `https://你的專案.supabase.co` | Supabase 網址 |
| `SUPABASE_KEY` | `eyJ...` | anon public key |
| `JINA_API_KEY` | `jina_...` | Jina AI API Key |
| `USE_VECTOR` | `true` | 開啟向量搜尋 |

### 4. Jina AI 申請
- 官網：https://jina.ai/embeddings/
- 註冊後取得 API Key
- **免費額度：200,000 tokens/月**

---

## 三、踩坑記錄

### ❌ Zeabur 不能跑 Ollama
- **問題**：Ollama 在 Zeabur 上會崩潰
- **原因**：Ollama 需要綁定特定 IP，但 Zeabur 的網絡不支持
- **解決**：改用 Jina AI（免費向量 API）

### ❌ 向量維度錯誤
- **問題**：`expected 1536 dimensions, not 768`
- **原因**：Supabase 設成 1536（OpenAI），但 Jina 是 768 維
- **解決**：用 SQL 重新設定為 768 維

### ❌ API Key 不能存 GitHub
- **問題**：直接將 API Key 寫入 .env.example
- **解決**：.env.example 只放範例，用戶自己填

---

## 四、OpenClaw 連接

### 方式
在 OpenClaw 的設定畫面中：

| 設定 | 值 |
|------|-----|
| Brain API URL | `https://supabase-20260318.zeabur.app` |

---

## 五、API 使用

### 新增文章
```bash
curl -X POST https://supabase-20260318.zeabur.app/ingest/article \
  -H "Content-Type: application/json" \
  -d '{
    "title": "標題",
    "raw_content": "內文",
    "summary": "摘要",
    "tags": ["tag1", "tag2"]
  }'
```

### 搜尋文章
```bash
curl -X POST https://supabase-20260318.zeabur.app/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "關鍵詞",
    "top_k": 3
  }'
```

### 刪除文章
```bash
curl -X DELETE https://supabase-20260318.zeabur.app/article/{article_id}
```

---

## 六、相關連結

- Supabase: https://supabase.com
- Jina AI: https://jina.ai/embeddings/
- GitHub Repo: https://github.com/yuutachichao/supabase-20260318

---

## 七、部署檢查清單

- [ ] 申請 Supabase 帳號
- [ ] 建立專案並取得 API Key
- [ ] 執行 SQL 建立資料表（向量維度 768）
- [ ] 部署 supabase-20260318 到 Zeabur
- [ ] 設定環境變數
- [ ] 測試新增/搜尋/刪除
- [ ] 配置 OpenClaw 連線

---

*記錄時間：2026-03-18*
