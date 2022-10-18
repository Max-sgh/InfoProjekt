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
        # Links LDAP:
        #  - https://gist.github.com/ibeex/1288159 - einfache LDAP Anmeldung
        #  - https://blog.thomastoye.be/python-ldap-authentication-with-microsoft-active-directory-46661bebc483 - AD mit Python
        #  - https://soshace.com/integrate-ldap-authentication-with-flask/ - LDAP mit Flask
        #  - https://gist.github.com/mick-t/85fc40d1acaf5e98cad9 - Gruppen von Nutzer suchen
        #  - https://gist.github.com/dangtrinhnt/28ef75299618a1b52cf887592220489f - alle Gruppenmitglieder
        #  - https://stackoverflow.com/questions/16999627/ldap-server-which-is-my-base-dn - Base DN LDAP
        #  - https://support.infrasightlabs.com/help-pages/how-to-find-the-correct-base-dn-setting/ - Base DN in AD
        #  - https://stackoverflow.com/questions/1032351/how-to-write-ldap-query-to-test-if-user-is-member-of-a-group - Testen ob Benutzer in Gruppe
        #  - https://stackoverflow.com/questions/18756688/what-are-cn-ou-dc-in-an-ldap-search - Abkürzungen in LDAP
        #  - https://www.faq-o-matic.net/2008/01/13/ldap-grundlagen-fuer-active-directory/ - LDAP Grundlagen für AD
        #  - https://www.faq-o-matic.net/2002/09/21/active-directory-ldap-feldnamen/ - AD Feldnamen
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
    schueler = []
    schueler.append(["Aico", "Ailary", 1, "m", 100, "5a"])
    schueler.append(["Bico", "Bilary", 2, "w", 20, "5c"])
    schueler.append(["Cico", "Bilary", 3, "w", -10, "5a"])
    schueler.append(["Fico", "Nilary", 4, "m", 50, "5d"])
    schueler.append(["Hico", "Hilary", 5, "Seeadler", 5678, "0b"])
    schueler.append(["Zico", "Zilary", 6, "Seeadler", 101, "5a"])
    schueler.append(["Zaco", "Zalary", 7, "Seeadler", 5324, "5a"])

    return render_template("evaluation.html", schueler=schueler)

@app.route('/settings')
def settings():
    if request.args.get('section') == None:
        return render_template("settings.html", section="None")
    else:
        return render_template("settings.html", section=request.args.get('section'))

@app.route('/settings/class')
def settings_class():
    if request.args.get('class') == None:
        return redirect(url_for("home"))
    klasse = request.args.get('class')
    return render_template("settingsClass.html", klasse=klasse)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)