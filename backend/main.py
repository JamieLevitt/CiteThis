from multiprocessing import Process
from core import serverManager, app
from flask import url_for

if __name__ == "__main__":
    Process(target=app.run, kwargs=dict(debug=True)).start()
    Process(target=serverManager.main_loop(app)).start()