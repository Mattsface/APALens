import os

from flask import Flask, render_template

app = Flask(__name__)
app.config["APA_REFRESH_TOKEN"] = os.getenv("APA_REFRESH_TOKEN")


@app.route("/")
def index():
    return render_template("index.html")
