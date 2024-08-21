from datetime import datetime
import watcher
import logging


manager.Coordinator__Start()
from flask import request, Flask

app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.disabled = True


@app.route("", methods=["POST"])
def start_server():
    msg = request.form.get("msg") or ""
    if msg == "":
        pass
