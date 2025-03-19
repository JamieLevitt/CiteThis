from fastapi import APIRouter, Header, HTTPException, Depends

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from core.tools import update_trends, update_articles, purge_dead_entries

tasks_router = APIRouter()

def validate_oidc_token(token):
    try:
        expected_audience = "https://your-service-url" 
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), expected_audience)
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError("Wrong issuer")
        return id_info
    except ValueError as e:
        raise Exception("Invalid token") from e

async def require_oidc_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid auth header")
    token = authorization.split(" ")[1]
    return validate_oidc_token(token)


@tasks_router.get("/update_trends")
async def update_trends():
    # Now using await since get_trends_raw is async
    try:
        update_trends
        return {"status": "trends updated"}
    except Exception as e:
        return {"error": str(e)}

@tasks_router.get("/update_articles")
# @require_oidc
def update_articles_task():
    try:
        update_articles()
        return {"status": "articles updated"}
    except Exception as e:
        return {"error": str(e)}

@tasks_router.get("/tasks/purge")
# @require_oidc
def purge_task():
    try:
        purge_dead_entries()
        return {"status": "purge completed"}
    except Exception as e:
        return {"error": str(e)}