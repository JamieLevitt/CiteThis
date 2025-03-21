from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from .tasks import tasks_router
from structs.API import PostBody, APIResponse
from .tools import tag_post

# Initialize FastAPI application
app = FastAPI()

# Include the tasks router for task-related endpoints
app.include_router(tasks_router, prefix="/tasks")

# Add CORS middleware to allow requests from a specific origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://x.com"],  # Allowed origin
    allow_credentials=True,  # Allow credentials in CORS requests
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/analyse_post", response_model = APIResponse)
def analyse_post(post_body: PostBody):
    """
    Analyze a given post by extracting relevant tags from its text.
    
    Args:
        post_body (PostBody): The request body containing the post text.
    
    Returns:
        dict: A dictionary containing the extracted tags or an error message.
    """
    try:
        return tag_post(post_body.text)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = e)
