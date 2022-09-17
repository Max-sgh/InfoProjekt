from crypt import methods
from urllib import request
from flask import Flask, redirect, url_for, render_template, send_from_directory, request
import sqlite3

app = Flask(__name__, static_folder="icons")

@app.route('/')
def home():
    return "it works!"

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]
        #
        # Anmeldung durchführen
        #
        return redirect(url_for("home"))
    else:
        return render_template("login.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")