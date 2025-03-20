from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .tasks import tasks_router
from structs.core import PostBody, TrendData
from .tools import tag_post

app = FastAPI()
app.include_router(tasks_router, prefix="/tasks")

app = FastAPI()

# You can add additional URLs to this list, for example, the frontend's production domain, or other frontends.

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["https://x.com"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


@app.post("/analyse_post")
def analyse_post(post_body:PostBody):
    try:
        return tag_post(post_body.text)
    except Exception as e:
        return {"error": str(e)}