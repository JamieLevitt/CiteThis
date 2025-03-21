from fastapi import APIRouter

from core.tools import update_trends, update_articles, purge_dead_entries

# Create an API router for task-related endpoints
tasks_router = APIRouter()

# Called daily by Google Cloud Scheduler
@tasks_router.get("/update_trends")
async def async_update_trends() -> dict:
    """
    Asynchronously update trending topics.
    
    Returns:
        dict: Status message indicating success or failure.
    """
    try:
        await update_trends()
        return {"status": "trends updated"}
    except Exception as e:
        return {"error": str(e)}

# Called daily by Google Cloud Scheduler
@tasks_router.get("/update_articles")
def update_articles_task() -> dict:
    """
    Update articles by fetching new data.
    
    Returns:
        dict: Status message indicating success or failure.
    """
    try:
        update_articles()
        return {"status": "articles updated"}
    except Exception as e:
        return {"error": str(e)}

# Called daily by Google Cloud Scheduler
@tasks_router.get("/purge")
def purge_task() -> dict:
    """
    Purge outdated or invalid entries from the system.
    
    Returns:
        dict: Status message indicating success or failure.
    """
    try:
        purge_dead_entries()
        return {"status": "purge completed"}
    except Exception as e:
        return {"error": str(e)}