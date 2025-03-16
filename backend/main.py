import os
from core import app, serverManager
print("Running process:", os.getpid())

if __name__ == "__main__":
    print("Running process:", os.getpid())
    #serverManager.process_queue()
    # serverManager._update_trends()
    app.run()
    print("Running process:", os.getpid())