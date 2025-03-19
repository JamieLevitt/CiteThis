from core import app, serverManager
if __name__ == "__main__":
    serverManager.process_queue()
    app.run()