from fastapi import APIRouter, HTTPException

from core.tools import update_trends, update_articles, purge_dead_entries

# Create an API router for task-related endpoints
tasks_router = APIRouter()

# Called daily by Google Cloud Scheduler
@tasks_router.get("/update_trends")
async def update_trends_task() -> dict:
    """
    Asynchronously update trending topics.
    
    Returns:
        dict: Status message indicating success or failure.
    """
    try:
        await update_trends()
        return {"status": "trends updated"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = e)

# Called daily by Google Cloud Scheduler
@tasks_router.get("/update_articles")
def update_articles_task() -> dict:
    """
    Update trends' articles to latest available.
    
    Returns:
        dict: Status message indicating success or failure.
    """
    try:
        update_articles()
        return {"status": "articles updated"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = e)

# Called daily by Google Cloud Scheduler
@tasks_router.get("/purge")
def purge_task() -> dict:
    """
    Purge outdated entries from the system.
    
    Returns:
        dict: Status message indicating success or failure.
    """
    try:
        purge_dead_entries()
        return {"status": "purge completed"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = e)