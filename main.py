from crypt import methods
from urllib import request
from flask import Flask, redirect, url_for, render_template, send_from_directory, request
from datetime import date
import sqlite3

app = Flask(__name__, static_folder="static")

#
# https://www.bundesjugendspiele.de/handbuch/wettkampf-leichtathletik/auswertung-formeln-und-beispiele-zur-punkteberechnung/
#
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

@app.route('/settings/gradelevel')
def settings_gradelevel():
    if request.args.get('id') == None:
        return redirect(url_for("home"))
    klassenstufe = request.args.get("id")
    return render_template("settingsGradeLevel.html", klassenstufe = klassenstufe)

#
# API Requests
#
@app.route('/settings/class/getstudents')
def getUser():
    #
    # Alle Schüler der Klasse als JSON (?) zurückgeben
    #
    if request.args.get('klasse') == None:
        return "error"
    else: 
        klasse = request.args.get('klasse')
        print("Get User of class " + klasse)
        students = ""
        if klasse == "none":
            # Schüler ohne Klasse zurückgeben
            students = '{"students": [{"schuelerNr":"1" , "firstname":"Aico" , "lastname":"Aillary" , "geschlecht":"u"}, {"schuelerNr":"5" , "firstname":"Dico" , "lastname":"Dillary" , "geschlecht":"m"}, {"schuelerNr":"6" , "firstname":"Eico" , "lastname":"Eillary" , "geschlecht":"u"}]}'
        else:
            # Schüler einer bestimmte Klasse zurückgeben
            students = '{"students": [{"schuelerNr":"1" , "firstname":"Aico" , "lastname":"Aillary" , "geschlecht":"u"}, {"schuelerNr":"5" , "firstname":"Dico" , "lastname":"Dillary" , "geschlecht":"m"}]}'
        
        return students

@app.route('/settings/class/addstudent')
def addUser():
    #
    # Benutzer mit ID zu Klasse hinzufügen
    #
    if request.args.get('id') == None or request.args.get('klasse') == None:
        return "error"
    else: 
        id = request.args.get('id')
        klasse = request.args.get('klasse')
        print("Add user #" + id + " to Class " + klasse + "\n")
        return "success"

@app.route('/settings/class/removestudent')
def removeUser():
    #
    # Benutzer mit ID aus Klasse entfernen
    #
    if request.args.get('id') == None:
        return "error"
    else: 
        id = request.args.get('id')
        print("Remove user #" + id)
        return "success"

@app.route('/settings/gradelevel/getdisciplines')
def getdiscipline():
    #
    # eingetragene Disziplinen der Klassenstufe zurückgeben
    #
    if request.args.get('id') == None:
        return "error"
    else:
        # bei keinen vorhanden Disziplinen "" zurückgeben
        data = "sprint,50,h;laufen,1000;kugelstoss;schleuderball;ballwurf,200"
        return data

@app.route('/settings/gradelevel/removediscipline')
def removediscipline():
    #
    # Disziplin von Klassenstufe entfernen
    #
    if request.args.get('gradelevel') == None or request.args.get('discipline') == None:
        return "error"
    else:
        gradelevel = request.args.get('gradelevel')
        discipline = request.args.get('discipline')
        print("Remove discipline '" + discipline + "' from gradelevel #" + gradelevel)
        return "success"

@app.route('/settings/gradelevel/adddiscipline')
def adddiscipline():
    # 
    # Disziplin einer Klassenstufe hinzufügen
    #
    if request.args.get('data') == None:
        return "error"
    else:
        arg = request.args.get('data')
        data = arg.split(',')
        print("Add '" + data[1] + "' to Grade Level #" + data[0])
        gradelevel = data[0]
        discipline = data[1]
        if discipline == "sprint":
            distanz = data[2]
            messung = data[3]
            print("Sprint - " + distanz + "m " + messung)
        elif discipline == "laufen":
            distanz = data[2]
            print("Laufen " + distanz + "m")
        elif discipline == "ballwurf":
            gewicht = data[2]
            print("Ballwurf " + gewicht + "g")
        else:
            print("Andere Disziplin - " + discipline)
        return "success"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)