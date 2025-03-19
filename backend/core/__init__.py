from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .tasks import tasks_router
from structs.core import PostBody, TrendData
from .tools import tag_post

app = FastAPI()
app.include_router(tasks_router, prefix="/tasks")

#Allow for CORS requests
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyse_post", response_model=TrendData)
def analyse_post(post_body:PostBody):
    try:
        return tag_post(post_body.text)
    except Exception as e:
        return {"error": str(e)}