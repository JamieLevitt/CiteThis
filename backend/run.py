from core import app
import logging

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)
    except Exception as e:
        logging.warning(e)