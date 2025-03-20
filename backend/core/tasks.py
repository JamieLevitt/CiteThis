from fastapi import APIRouter, Header, HTTPException, Depends

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from core.tools import update_trends, update_articles, purge_dead_entries

tasks_router = APIRouter()

@tasks_router.get("/update_trends")
async def async_update_trends():
    try:
        await update_trends()
        return {"status": "trends updated"}
    except Exception as e:
        return {"error": str(e)}

@tasks_router.get("/update_articles")
def update_articles_task():
    try:
        update_articles()
        return {"status": "articles updated"}
    except Exception as e:
        return {"error": str(e)}

@tasks_router.get("/tasks/purge")
def purge_task():
    try:
        purge_dead_entries()
        return {"status": "purge completed"}
    except Exception as e:
        return {"error": str(e)}