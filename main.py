from crypt import methods
from urllib import request
from flask import Flask, redirect, url_for, render_template, send_from_directory, request
from datetime import date
import sqlite3

app = Flask(__name__, static_folder="static")

@app.route('/')
def home():
    station = "Wurf 1"
    return render_template("home.html", station=station)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]
        #
        # Anmeldung durchführen; Session Variablen setzen
        #
        return redirect(url_for("home"))
    else:
        return render_template("login.html")

@app.route('/class')
def detailClass():
    id = request.args.get('id')
    print(id)
    schueler = [["123456", "DomDom", "Georg"], ["234567", "sdfgh", "sedfgh"], ["123", "Göröp", "WOW"]]
    return render_template("detailClass.html", className="10a", schueler=schueler)

@app.route('/evaluation')
def evaluation():
    return render_template("evaluation.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)