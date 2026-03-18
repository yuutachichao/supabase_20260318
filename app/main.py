"""
Supabase + Ollama Knowledge Base API

使用本地 Ollama 生成向量，存儲到 Supabase
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client

app = FastAPI(title="Supabase + Ollama Knowledge Base API")

# 環境變數
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
USE_VECTOR = os.getenv("USE_VECTOR", "false").lower() == "true"

# 初始化 Supabase client
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_embedding(text: str) -> Optional[List[float]]:
    """使用 Ollama 生成向量"""
    if not USE_VECTOR:
        return None
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": OLLAMA_MODEL, "prompt": text},
            timeout=60
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None


# --- Pydantic Models ---

class ArticleIn(BaseModel):
    title: str
    raw_content: str
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = "web"
    language: Optional[str] = "zh-TW"


class ArticleOut(BaseModel):
    id: str
    title: str
    summary: Optional[str]
    tags: Optional[List[str]]
    created_at: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


class SearchResult(BaseModel):
    id: str
    title: str
    summary: Optional[str]
    tags: Optional[List[str]]
    similarity: float = 1.0


# --- API Endpoints ---

@app.get("/")
async def root():
    return {
        "status": "ok", 
        "message": "Supabase + Ollama Knowledge Base API",
        "vector_enabled": USE_VECTOR
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/ingest/article", response_model=Dict)
async def ingest_article(article: ArticleIn):
    """新增文章（可選生成向量）"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    try:
        embedding = None
        if USE_VECTOR:
            text_to_embed = f"{article.title} {article.summary or ''} {article.raw_content[:1000]}"
            embedding = get_embedding(text_to_embed)
        
        # 準備資料
        data = {
            "id": str(uuid.uuid4()),
            "title": article.title,
            "raw_content": article.raw_content,
            "summary": article.summary,
            "key_points": json.dumps(article.key_points) if article.key_points else None,
            "tags": article.tags,
            "source_url": article.source_url,
            "source_type": article.source_type,
            "language": article.language,
        }
        
        if embedding:
            data["embedding"] = embedding
        
        # 存入 Supabase
        result = supabase.table("articles").insert(data).execute()
        
        return {"ok": True, "article_id": data["id"]}
        
    except Exception as e:
        print(f"Error ingesting article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/article/{article_id}", response_model=Dict)
async def delete_article(article_id: str):
    """刪除文章"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    try:
        result = supabase.table("articles").delete().eq("id", article_id).execute()
        return {"ok": True, "deleted": article_id}
    except Exception as e:
        print(f"Error deleting article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=List[SearchResult])
async def search_articles(search_req: SearchRequest):
    """搜尋文章"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    # 如果有啟用向量搜尋
    if USE_VECTOR:
        try:
            query_embedding = get_embedding(search_req.query)
            if query_embedding:
                result = supabase.rpc(
                    "match_articles",
                    {
                        "query_embedding": query_embedding,
                        "match_threshold": 0.5,
                        "match_count": search_req.top_k
                    }
                ).execute()
                
                results = []
                for item in result.data:
                    results.append(SearchResult(
                        id=item["id"],
                        title=item["title"],
                        summary=item.get("summary"),
                        tags=item.get("tags"),
                        similarity=item.get("similarity", 0)
                    ))
                return results
        except Exception as e:
            print(f"Vector search error: {e}")
    
    # Fallback: 簡單的文字搜尋
    try:
        # 搜尋標題
        result = supabase.table("articles").select("*").ilike("title", f"%{search_req.query}%").execute()
        
        results = []
        for item in result.data[:search_req.top_k]:
            results.append(SearchResult(
                id=item["id"],
                title=item["title"],
                summary=item.get("summary"),
                tags=item.get("tags"),
                similarity=1.0
            ))
        
        # 如果標題沒找到，搜尋內容
        if not results:
            result = supabase.table("articles").select("*").ilike("raw_content", f"%{search_req.query}%").execute()
            for item in result.data[:search_req.top_k]:
                results.append(SearchResult(
                    id=item["id"],
                    title=item["title"],
                    summary=item.get("summary"),
                    tags=item.get("tags"),
                    similarity=0.8
                ))
        
        return results
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
