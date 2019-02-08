from flask import Flask

app = Flask(__name__)

@app.route("/")
def accept_client():
    return "Accepted client."
