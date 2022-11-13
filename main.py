from urllib import request
#import ldap
from flask import Flask, redirect, url_for, render_template, send_from_directory, request, session
from datetime import date
import sqlite3

#'Schuelernummer','Jahrgang','Klasse','Geschlecht', Fahrschüler(unnötig),'Name','Vorname', 'Geburtsdatum'

from sprint import Sprint
from ldapUtils import ldapUtils


app = Flask(__name__, static_folder="static")
# Sicherheitsschlüssel zur Verschlüsselung der Sessions setzen
app.secret_key = "Göröp"

#Einstellungen
_cnAdminGruppe = "Sportfest"
_adBaseDN = "DC=srv-lange,DC=de"
_adServer = "192.168.178.54"
_adAdminUser = "Administrator@srv-lange.de"
_adPasswort = "Rsu3sc123"
_domainName = "srv-lange.de"

#ldap = ldapUtils("DC=srv-lange,DC=de", "192.168.178.54", "Administrator@srv-lange.de", "Rsu3sc123")
_ldapU = ldapUtils(_adBaseDN, _adServer, _adAdminUser, _adPasswort)
#conn, success = _ldapU.authenticate("test@srv-lange.de", "Rsu3sc123&")
#conn.unbind()
# return [cn, vorname, nachname, loginName, anzeigeName]
#_ldapU.getUserDetail("lehrer1")
#if _ldapU.checkGroup("lehrer1", "Sportfest"):
#    print("Yeah")
#else: 
#    print("Neay")
#_ldapU.getAllGroupMembers("Sportfest") #['lehrer2', 'lehrer1']

def checkLogin() -> bool:
    if not "user" in session:
        return False
    else:
        return True

def checkAdmin():
    if checkLogin() and "admin" in session and session["admin"] == True:
        return True
    else:
        return False

def berechnePunkte(stationID, wert, schuelerNr):
    punkte = 0
    #
    # Disziplin über stationID ermitteln und fehlende Werte ergänzen
    #
    disziplin = "sprint50"
    messung = "h"
    if disziplin.startswith('sprint'):
        distanz = int(disziplin.split('sprint')[1])
    if  disziplin.startswith('laufen'):
        distanz = int(disziplin.split('laufen')[1])
    if  disziplin.startswith('ballwurf'):
        gewicht = int(disziplin.split('ballwurf')[1])
    #
    # Geschlecht über Schülernummer bestimmen
    #
    geschlecht = 'm'

    if disziplin.startswith('sprint'):
        punkte = Sprint().berechnePunkte(wert, geschlecht, messung, distanz)

    return punkte


#
# Routen 
#
# https://www.bundesjugendspiele.de/handbuch/wettkampf-leichtathletik/auswertung-formeln-und-beispiele-zur-punkteberechnung/
@app.route('/')
def home():
    #
    # Startseite
    #
    if not checkLogin():
        return redirect(url_for("login"))
    station = session["station"]
    stationID = session["stationID"]
    #station = "none"
    # Alle Klassen, die der Station mit gegebener ID zugeteilt wurden, aus DB holen und in Array einfügen
    klassen = [["10a", 22, "true"], ["8a", 32, "false"], ["5d", 15, "false"]]
    return render_template("home.html", station=station, classes = klassen)

@app.route("/login", methods=["POST", "GET"])
def login():
    #
    # Loginseite (GET) / Auswertung der eingegebenen Logindaten(POST)
    # 
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]
        #
        # Anmeldung durchführen
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

        # Benutzername und Passwort prüfen; auf Administratorrechte im System prüfen
        if user == "admin" and password == "admin":
            session["user"] = user
            session["admin"] = True
        else:
            conn, success = _ldapU.authenticate(user + "@" + _domainName, password)
            if success and _ldapU.checkGroup(user, "Lehrer"):
                session["user"] = user
                if _ldapU.checkGroup(user, "Sportfest"):
                    session["admin"] = True
                else:
                    session["admin"] = False
            else: 
                return render_template("login.html", error=True)

        #Station von DB holen - bei keiner Zuteilung station="none"
        session["station"] = "Sprint 1"
        session["stationID"] = "sprint1" # ???

        return redirect(url_for("home"))
    else:
        if checkLogin():
            return redirect(url_for("home"))
        return render_template("login.html")

@app.route('/class')
def detailClass():
    # 
    # Klassenanzeige zum Eintragen der Werte für zugewiesenen Lehrer
    #
    if not checkLogin():
        return redirect(url_for("login"))

    if request.args.get('id') == None:
        return redirect(url_for("home"))
    else: 
        id = request.args.get('id')
        print(id)
        schueler = [["123456", "DomDom", "Georg"], ["234567", "sdfgh", "sedfgh"], ["123", "Göröp", "WOW"]]
        return render_template("detailClass.html", className="10a", schueler=schueler, discipline="sprint")

@app.route('/student')
def detailStudent():
    # 
    # Einzelansicht eines Schülers mit eingetragenen Werten und Stammdaten
    #
    if not checkAdmin():
        return redirect(url_for("login"))

    if request.args.get('id') == None:
        return redirect(url_for("home"))
    else: 
        schuelerNr = request.args.get('id')
        return render_template("detailStudent.html")

@app.route('/evaluation')
def evaluation():
    # 
    # Seite zur Auswertung aller Schüler
    #
    if not checkAdmin():
        return redirect(url_for("login"))

    # Alle Schüler aus DB holen und Werte in Array einfügen
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
    # 
    # Einstellungsmenü
    #
    if not checkAdmin():
        return redirect(url_for("login"))

    if request.args.get('section') == None:
        return render_template("settings.html", section="None")
    else:
        return render_template("settings.html", section=request.args.get('section'))

@app.route('/settings/class')
def settings_class():
    #
    # Einstellungen für einzelne Klassen
    #
    if not checkAdmin():
        return redirect(url_for("login"))

    if request.args.get('class') == None:
        return redirect(url_for("home"))
    klasse = request.args.get('class')
    return render_template("settingsClass.html", klasse=klasse)

@app.route('/settings/gradelevel')
def settings_gradelevel():
    #
    # Einstellungen für Klassenstufen
    #
    if not checkAdmin():
        return redirect(url_for("login"))

    if request.args.get('id') == None:
        return redirect(url_for("home"))
    klassenstufe = request.args.get("id")
    return render_template("settingsGradeLevel.html", klassenstufe = klassenstufe)

@app.route('/settings/station')
def settings_station():
    #
    # Einstellungen für Station
    #
    if not checkAdmin():
        return redirect(url_for("login"))

    if request.args.get('id') == None:
        return redirect(url_for("home"))
    stationID = request.args.get("id")
    return render_template("settingsStation.html", stationID = stationID)

#
# API Requests
#
@app.route('/settings/class/getstudents')
def getUser():
    #
    # Alle Schüler der Klasse als JSON (?) zurückgeben
    #
    if not checkAdmin():
        return "error"
    
    if request.args.get('klasse') == None:
        return "error"
    else: 
        klasse = request.args.get('klasse')
        print("Get User of class " + str(klasse))
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
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None or request.args.get('klasse') == None:
        return "error"
    else: 
        id = request.args.get('id')
        klasse = request.args.get('klasse')
        print("Add user #" + str(id) + " to Class " + str(klasse))
        return "success"

@app.route('/settings/class/removestudent')
def removeUser():
    #
    # Benutzer mit ID aus Klasse entfernen
    #
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else: 
        id = request.args.get('id')
        print("Remove user #" + str(id))
        return "success"

@app.route('/settings/gradelevel/getdisciplines')
def getdiscipline():
    #
    # eingetragene Disziplinen der Klassenstufe zurückgeben
    #
    if not checkAdmin():
        return "error"

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
    if not checkAdmin():
        return "error"

    if request.args.get('gradelevel') == None or request.args.get('discipline') == None:
        return "error"
    else:
        gradelevel = request.args.get('gradelevel')
        discipline = request.args.get('discipline')
        print("Remove discipline '" + str(discipline) + "' from gradelevel #" + str(gradelevel))
        return "success"

@app.route('/settings/gradelevel/adddiscipline')
def adddiscipline():
    # 
    # Disziplin einer Klassenstufe hinzufügen
    #
    if not checkAdmin():
        return "error"

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

@app.route('/class/addvalue')
def addValue():
    if not checkLogin():
        return "error"

    if request.args.get('id') == None or request.args.get('stationsid') == None or request.args.get('value') == None:
        return "error"
    else:
        schuelerNr = request.args.get('id')
        stationsId = request.args.get('stationsid')
        value = request.args.get('value')
        print(str(schuelerNr) + " an Station " + str(stationsId) + "; Wert: " + str(value))
        return "success - " + str(schuelerNr)

@app.route('/student/changeData', methods=["POST"])
def changeStudentData():
    if not checkAdmin():
        return "error"

    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        schuelerNr = request.form["id"]
        print(firstname + " " + lastname + " " + schuelerNr)
        return "success"

@app.route('/student/getmeasurements')
def getMeasurements():
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else:
        #
        # Alle eingetragenen Werte für Schüler mit SchülerNr = id zurückgeben.
        # Bei Disziplin ohne Werte "none" einsetzen.
        #
        # Daten im TSV Format - letzter Buchstabe muss \n sein.
        #
        ret = "sprint50\t12,5\t512\nlaufen1000\t5,25\t300\nkugelstoss\t6,5\t520\n"
        return ret

@app.route('/student/changemeasurements', methods=["POST"])
def changemeasurements():
    if not checkAdmin():
        return "error"
    
    if request.method == "POST":
        string = request.form["string"]
        schuelerNr = request.form["id"]
        disciplines = string.split("\n")
        disciplines.pop()
        for d in disciplines:
            print (d)
            discipline = d.split('\t')[0]
            value = d.split('\t')[1]
            #
            # Disziplin und Wert in DB ändern
            # Neue Punktzahl berechnen
            #
        return "success"

@app.route('/student/delete')
def deleteStudent():
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else:
        # 
        # Schüler in Tabelle Schüler löschen 
        # Alle Werte von Schüler löschen
        #
        return "success"

@app.route('/station/getClasses')
def get_classes():
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else:
        if request.args.get('discipline') == None:
            # Alle Klassen der Station
            return "10a;closed\n5b;open\n"
        else:
            # Alle Klassen mit Disziplin = discipline, die NICHT in Station sind
            dicipline = request.args.get('discipline')
            return "5b\n8a\n12c\n25a\n"

@app.route('/station/getDetails')
def get_details():
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else:
        return "Wurf 1\nballwurf200\nReD\nChristin Redlich"

@app.route('/station/getTeacher')
def add_class():
    if not checkAdmin():
        return "error"
    
    if request.args.get('id') == None:
        return "error"
    else:
        #
        # Alle Lehrer ohne Station und Lehrer der Station zurück geben
        #
        return "WaG;Torsten Wagner\nBeM;Chris Bergmann\nReD;Christin Redlich\n"

@app.route('/station/changeData', methods=["POST"])
def change_data():
    if not checkAdmin():
        return "error"
    if request.method == "POST":
        lehrer = request.form["lehrer"]
        name = request.form["name"]
        stationID = request.form["id"]
        return "success"

@app.route('/station/addClass', methods=["POST"])
def add_class_station():
    if not checkAdmin():
        return "error"
    if request.method == "POST":
        klasse = request.form["class"]
        stationID = request.form["id"]
        print(stationID + " -> " + klasse)
        return "success"

@app.route('/station/deleteClass')
def delete_class_station():
    if not checkAdmin():
        return "error"
    if request.args.get('id') == None or request.args.get('class') == None:
        return "error"
    else:
        stationID = request.args.get('id')
        klasse = request.args.get('class')
        print("Delete: " + stationID + " -> " + klasse)
        return "success"

@app.route('/station/deleteStation')
def delete_station():
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else:
        return "success"

@app.route('/station/addStation', methods=["POST"])
def add_station():
    if not checkAdmin():
        return "error"
    if request.method == "POST":
        name = request.form["name"]
        discipline = request.form["discipline"]
        teacher = request.form["teacher"]
        print("Neue Station: " + name + " - " + discipline + " -> " + teacher)
        return "success"

@app.route('/logout')
def logout():
    session.pop("user", None)
    session.pop("station", None)
    session.pop("stationID", None)
    session.pop("admin", None)
    return redirect(url_for("login"))

@app.route('/user/isadmin')
def isAdmin():
    if checkAdmin():
        return "true"
    else:
        return "false"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)