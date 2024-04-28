# run.py
from gevent import monkey

monkey.patch_all()

from gunicorn.app.base import BaseApplication
from gunicorn.workers.ggevent import GeventWorker
from api import app  # Import your Flask application


class FlaskApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.application = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key, value)

    def load(self):
        return self.application


if __name__ == "__main__":
    options = {
        "bind": "localhost:8003",
        "worker_class": "gevent",
        "workers": 15,  # Change the number of workers here
        "accesslog": "-",
    }
    FlaskApplication(app, options).run()
