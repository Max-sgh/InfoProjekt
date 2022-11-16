from urllib import request
import ldap
from flask import Flask, redirect, url_for, render_template, send_from_directory, request, session
from datetime import date
import sqlite3
import re

from server import Server

app = Flask(__name__, static_folder="static")
# Sicherheitsschlüssel zur Verschlüsselung der Sessions setzen
app.secret_key = "Göröp"

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
    # Alle Klassen, die der Station mit gegebener ID zugeteilt wurden, aus DB holen und in Array einfügen
    klassen = []
    dbCon, dbCur = _server.getDB()
    results = dbCur.execute("SELECT Name FROM station WHERE StationID='" + str(stationID) + "';").fetchall()
    if len(results) == 0:
        return render_template("home.html", station=station, classes = [])
    name = results[0][0]
    zuweisungen = dbCur.execute("SELECT Klasse, Status FROM zuweisungStation WHERE StationID=" + str(stationID)).fetchall()
    if len(zuweisungen) == 0:
        return render_template("home.html", station=station, classes = [])
    for zuweisung in zuweisungen:
        status = zuweisung[1] 
        if status == "open":
            status = "false"
        else:
            status = "true"
        klasse = zuweisung[0]
        schueler = dbCur.execute("SELECT SchuelerNr FROM schueler WHERE Klasse='" + klasse + "';").fetchall()
        anzahl = len(schueler)
        if anzahl == 0:
            status = "true"
        klassen.append([klasse, anzahl, status])


    return render_template("home.html", station=station, classes = klassen)

@app.route("/login", methods=["POST", "GET"])
def login():
    #
    # Loginseite (GET) / Auswertung der eingegebenen Logindaten(POST)
    # 
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]
        print(user + " " + password)
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
            conn, success = _server._ldapU.authenticate(user + _server._domainName, password)
            if success and _server._ldapU.checkGroup(user, _server._cnUserGruppe):
                session["user"] = user
                if _server._ldapU.checkGroup(user, _server._cnAdminGruppe):
                    session["admin"] = True
                else:
                    session["admin"] = False
            else:
                return render_template("login.html", error=True)

        #Station von DB holen - bei keiner Zuteilung station="none"
        dbCon, dbCur = _server.getDB()
        results = dbCur.execute("SELECT Name,StationID FROM station WHERE lehrer='" + str(user) + "';").fetchall()
        if len(results) > 1:
            return "Error"
        if len(results) == 0:
            session["station"] = "none"
            session["stationID"] = "none"
        else:
            session["station"] = results[0][0]
            session["stationID"] = results[0][1]
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
        schueler = []
        dbCon, dbCur = _server.getDB()
        results = dbCur.execute("SELECT SchuelerNr, Vorname, Name FROM schueler WHERE Klasse='" + str(id) + "';").fetchall()
        if len(results) == 0:
            render_template("detailClass.html", className=id, schueler=[])
        for res in results:
            schuelerNr = res[0]
            vorname = res[1]
            nachname = res[2]
            schueler.append([schuelerNr, vorname, nachname])
        return render_template("detailClass.html", className=id, schueler=schueler)

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
        return render_template("detailStudent.html", schuelerNr = schuelerNr)

@app.route('/evaluation')
def evaluation():
    # 
    # Seite zur Auswertung aller Schüler
    #
    if not checkAdmin():
        return redirect(url_for("login"))

    # Alle Schüler aus DB holen und Werte in Array einfügen
    schueler = []
    """schueler.append(["Aico", "Ailary", 1, "m", 100, "5a"])
    schueler.append(["Bico", "Bilary", 2, "w", 20, "5c"])
    schueler.append(["Cico", "Bilary", 3, "w", -10, "5a"])
    schueler.append(["Fico", "Nilary", 4, "m", 50, "5d"])
    schueler.append(["Hico", "Hilary", 5, "Seeadler", 5678, "0b"])
    schueler.append(["Zico", "Zilary", 6, "Seeadler", 101, "5a"])
    schueler.append(["Zaco", "Zalary", 7, "Seeadler", 5324, "5a"])"""
    dbCon, dbCur = _server.getDB()
    results = dbCur.execute("SELECT SchuelerNr, Vorname, Name, Geschlecht, Klasse FROM schueler").fetchall()
    if len(results) == 0:
        render_template("evaluation.html", schueler=schueler)
    for res in results:
        schuerlerNr = res[0]
        vorname = res[1]
        nachname = res[2]
        geschlecht = res[3]
        klasse = res[4]
        punkte = 0
        werte = dbCur.execute("SELECT StationID, Wert FROM wert WHERE SchuelerNr=" + str(schuerlerNr)).fetchall()
        if len(werte) == 0:
            punkte = 0
        else:
            for w in werte:
                punkte += _server.berechnePunkte(w[0], w[1], schuerlerNr)
        schueler.append([vorname, nachname, schuerlerNr, geschlecht, punkte, klasse])


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
        dbCon, dbCur = _server.getDB()
        results = dbCur.execute("SELECT SchuelerNr, Vorname, Name, Geschlecht FROM schueler WHERE klasse='" + klasse + "';").fetchall()
        if len(results) == 0:
            return '{"students": []}'
        students = '{"students": ['
        for res in results:
            students += '{"schuelerNr":"' + str(res[0]) + '" , "firstname":"' + str(res[1]) + '" , "lastname":"' + str(res[2]) + '" , "geschlecht":"' + str(res[3]) + '"},'
        students = students[:-1]
        students += ']}'
        dbCur.close()
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
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("UPDATE schueler SET klasse='" + klasse + "' WHERE SchuelerNr=" + id)
            dbCon.commit()
            dbCon.close()
        except:
            return "error"
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
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("UPDATE schueler SET klasse='None' WHERE SchuelerNr=" + id)
            dbCon.commit()
            dbCon.close()
        except:
            return "error"
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
        klassenstufe = request.args.get('id')
        data = ""
        dbCon, dbCur = _server.getDB()
        results = dbCur.execute("SELECT Disziplin,Messung FROM disziplin WHERE Klassenstufe=" + klassenstufe).fetchall()
        if len(results) == 0:
            return ""
        for r in results:
            disziplin = r[0]
            messung = r[1]
            data += disziplin + "," + messung + ";"
        data = data[:-1]
        #data = "sprint50,h;laufen800/1000;kugelstoss;schleuderball;ballwurf200"
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
        try:
            dbCon, dbCur = _server.getDB()
            results = dbCur.execute("SELECT DisziplinID FROM disziplin WHERE Klassenstufe=" + gradelevel + " AND Disziplin='" + discipline + "';").fetchall()
            if len(results) == 0:
                return "error"
            disziplinID = results[0][0]
            print(disziplinID)
            dbCur.execute("DELETE FROM disziplin WHERE Disziplin='" + discipline + "' AND Klassenstufe=" + str(gradelevel))
            dbCur.execute("DELETE FROM wert WHERE DisziplinID=" + str(disziplinID))
            dbCon.commit()
            dbCon.close()
        except:
            return "error"
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
        messung = "None"
        if discipline == "sprint50" or discipline == "sprint75" or discipline == "sprint100":
            #distanz = data[2]
            messung = data[2]
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("INSERT INTO disziplin (Disziplin, Klassenstufe, Messung) VALUES ('" + discipline + "'," + gradelevel + ",'" + messung + "')")
            dbCon.commit()
            dbCon.close()
        except:
            return "error"

        return "success"

@app.route('/settings/gradelevel/deleteClass')
def delete_class_gradelevel():
    if not checkAdmin():
        return "error"
    print(1)
    if request.args.get('class') == None:
        return "error"
    else:
        # Klasse löschen, allen Schüler der Klasse keine eintragen
        klasse = request.args.get('class')
        print(1)
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("DELETE FROM klasse WHERE Name='" + klasse + "'")
            dbCon.commit()
            print(1)

            for schueler in dbCur.execute("SELECT SchuelerNr FROM schueler WHERE Klasse='" + klasse + "'").fetchall():
                print(schueler[0])
                dbCon, dbCur = _server.getDB()
                dbCur.execute("UPDATE schueler SET klasse='None' WHERE SchuelerNr=" + str(schueler[0]) + ";")
                dbCon.commit()

            dbCon.close()
        except:
            return "error"

        return "success"

@app.route('/settings/gradelevel/getClasses')
def get_classes_gradelevel():
    if not checkAdmin():
        return "error"

    dbCon, dbCur = _server.getDB()
    res = dbCur.execute("SELECT Name, Klassenstufe FROM klasse;")
    if res.fetchone() is None:
        print("Error! No Classes")
        return "None;None,0"
    klassenstufen = [5,6,7,8,9,10]
    klassen = [[],[],[],[],[],[]]
    for f in dbCur.execute("SELECT Name, Klassenstufe FROM klasse;"):
        klassenstufe = f[1]
        klasse = f[0]
        index = klassenstufen.index(klassenstufe)
        klassen[index].append(klasse)
    ret = ""
    i = 0
    for klasse in klassen:
        ret += str(klassenstufen[i]) + ";"
        for k in klasse:
            ret += str(k) + "," + str(len(dbCur.execute("SELECT SchuelerNr FROM schueler WHERE klasse='" + k + "';").fetchall())) + ";"
        ret = ret[:-1]
        ret += "\n"
        i += 1
    ret += "None;None," + str(len(dbCur.execute("SELECT SchuelerNr FROM schueler WHERE klasse='None';").fetchall()))
    dbCur.close()
    #return "5;5a,10;5b,20;5b,9;5c,8;5d,30\n6;6a,20;6b,30;6c,5;6d,65\n7;7a,76;7b,2;7c,1\n8;8a,5;8b,87;8c,9\n9\n10\nNone;None,8"
    return ret

@app.route('/settings/gradelevel/addClass', methods=["POST"])
def add_class_gradelevel():
    if not checkAdmin():
        return "error"
    if request.method == "POST":
        gradelevel = request.form["gradelevel"]
        klasse = request.form["class"]
        print("Neue Klasse in #" + gradelevel + ": " + klasse)
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("INSERT INTO klasse (Name, Klassenstufe) VALUES ('" + klasse + "', " + gradelevel + ")")
            dbCon.commit()
            dbCon.close()
        except: 
            return "error"
        return "success"


@app.route('/class/addvalue')
def addValue():
    if not checkLogin():
        return "error"

    if request.args.get('id') == None or request.args.get('value') == None:
        return "error"
    else:
        schuelerNr = request.args.get('id')
        stationsId = session["stationID"]
        value = request.args.get('value')
        print(str(schuelerNr) + " an Station " + str(stationsId) + "; Wert: " + str(value))
        try:
            dbCon, dbCur = _server.getDB()
            results = dbCur.execute("SELECT Klasse FROM schueler WHERE SchuelerNr=" + str(schuelerNr)).fetchall()
            if len(results) != 1:
                return "error"
            klasse = results[0][0]
            dbCur.execute("INSERT INTO wert (StationID, SchuelerNr, Wert) VALUES(" + str(stationsId) + "," + str(schuelerNr) + ",'" + str(value) + "')")
            print(stationsId)
            dbCur.execute("UPDATE zuweisungStation SET Status='closed' WHERE StationID=" + str(stationsId) + " AND Klasse='" + klasse + "'")
            dbCon.commit()
            dbCon.close()
        except:
            print("Error")
            return "error"

        return "success - " + str(schuelerNr)

@app.route('/student/changeData', methods=["POST"])
def changeStudentData():
    if not checkAdmin():
        return "error"

    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        schuelerNr = request.form["id"]
        gender = request.form["gender"]
        print(firstname + " " + lastname + " " + schuelerNr + " " + gender)
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("UPDATE schueler SET Vorname='" + firstname + "', name='" + lastname + "', Geschlecht='" + gender + "' WHERE SchuelerNr=" + str(schuelerNr))
            dbCon.commit()
            dbCon.close()
        except:
            return "error"
        return "success"

@app.route('/student/getDetails')
def get_student_details():
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else:
        dbCon, dbCur = _server.getDB()
        results = dbCur.execute("SELECT Vorname, Name, Klasse, Geschlecht FROM schueler WHERE SchuelerNr=" + request.args.get('id')).fetchall()
        if len(results) != 1:
            return ""
        schueler = results[0]
        return schueler[0] + ";" + schueler[1] + ";" + schueler[2] + ";" + schueler[3]

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
        dbCon, dbCur = _server.getDB()
        results = dbCur.execute("SELECT Klasse FROM schueler WHERE SchuelerNr=" + str(request.args.get('id'))).fetchall()
        if len(results) != 1:
            return "error"
        klasse = results[0][0]
        if klasse == "None":
            return ""
        results = dbCur.execute("SELECT Klassenstufe FROM Klasse WHERE Name='" + klasse + "';").fetchall()
        if len(results) != 1:
            return "error1"
        klassenstufe = results[0][0]
        results = dbCur.execute("SELECT Disziplin FROM disziplin WHERE Klassenstufe=" + str(klassenstufe)).fetchall()
        if len(results) == 0:
            return ""
        disziplinen = []
        for res in results:
            disziplinen.append(res[0])
        ret = ""
        results = dbCur.execute("SELECT StationID, Wert, ID FROM wert WHERE schuelerNr=" + str(request.args.get('id'))).fetchall()
        for res in results:
            disziplin = dbCur.execute("SELECT Disziplin FROM station WHERE StationID=" + str(res[0])).fetchall()[0][0]
            if disziplin in disziplinen:
                disziplinen.remove(disziplin)
            wert = res[1]
            if not disziplin.startswith("laufen"):
                wert = float(res[1])
            ret += disziplin + "\t" + str(res[1]) + "\t" + str(_server.berechnePunkte(res[0], wert, request.args.get('id'))) + "\t" + str(res[2]) + "\n"
        for d in disziplinen:
            ret += d + "\tnone\n"
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
            ID = d.split('\t')[0]
            value = d.split('\t')[1]
            #
            # Disziplin und Wert in DB ändern
            # Neue Punktzahl berechnen
            #
            if ID == "none":
                # 
                # Neuen Wert anlegen
                #
                value = d.split("\t")[2]
                dbCon, dbCur = _server.getDB()
                results = dbCur.execute("SELECT Klasse FROM schueler WHERE SchuelerNr=" + str(request.args.get('id'))).fetchall()
                if len(results) != 1:
                    return "error"
                klasse = results[0][0]
                results = dbCur.execute("SELECT StationID FROM station WHERE Disziplin='" + d.split("\t")[1] + "'").fetchall()
                if len(results) == 0:
                    print("Eror1")
                    return "error"
                stationID = -1
                for s in results:
                    sID = s[0]
                    print(sID, klasse)
                    res = dbCur.execute("SELECT Status FROM zuweisungStation WHERE StationID=" + str(sID) + " AND Klasse='" + klasse + "'").fetchall()
                    print(len(res))
                    if len(res) == 1:
                        stationID = sID
                        break
                if stationID == -1:
                    return "error"
                try:
                    dbCur.execute("INSERT INTO wert (StationID, SchuelerNr, Wert) VALUES (" + str(stationID) + "," + str(schuelerNr) + ",'" + str(value) + "')").fetchall()
                    dbCon.commit()
                    dbCon.close()
                except:
                    print("Error")
                    return "error"

                return "success"

            try:
                dbCon, dbCur = _server.getDB()
                dbCur.execute("UPDATE wert SET Wert='" + value + "' WHERE ID=" + str(ID))
                dbCon.commit()
                dbCon.close()
            except:
                print("Error")
                return "error"

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
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("DELETE FROM wert WHERE SchuelerNr=" + str(request.args.get('id')))
            dbCur.execute("DELETE FROM schueler WHERE SchuelerNr=" + str(request.args.get('id')))
            dbCon.commit()
            dbCon.close()
        except:
            print("Error")
            return "error"
        return "success"

@app.route('/settings/getStations')
def get_stations():
    if not checkAdmin():
        return "error"
    dbCon, dbCur = _server.getDB()
    ret = ""
    results = dbCur.execute("SELECT StationID, Lehrer, Disziplin, Name From station;").fetchall()
    if len(results) == 0:
        return ""
    for r in results:
        id = r[0]
        lehrer = r[1]
        disziplin = r[2]
        name = r[3]
        status = "closed"
        res = dbCur.execute("SELECT Status FROM zuweisungStation WHERE StationID=" + str(id)).fetchall()
        if len(res) == 0:
            status = "open"
        else:
            for s in res:
                if s[0] == "open":
                    status = "open"
                    break
        ret += str(id) + ";" + name + ";" + disziplin + ";" + lehrer + ";" + status + "\n"
    print(ret)
    return ret

@app.route('/station/getClasses')
def get_classes():
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else:
        stationID = request.args.get('id')
        if request.args.get('discipline') == None:
            # Alle Klassen der Station
            dbCon, dbCur = _server.getDB()
            results = dbCur.execute("SELECT Klasse,Status FROM zuweisungStation WHERE StationID=" + stationID).fetchall()
            if len(results) == 0:
                return ""
            ret = ""
            for r in results:
                ret += r[0] + ";" + r[1] + "\n"
            return ret
        else:
            # Alle Klassen mit Disziplin = discipline, die NICHT in Station sind
            discipline = request.args.get('discipline')
            dbCon, dbCur = _server.getDB()
            results = dbCur.execute("SELECT Klassenstufe FROM disziplin WHERE Disziplin='" + discipline + "'").fetchall()
            if len(results) == 0:
                return ""
            stationen = []
            res = dbCur.execute("SELECT StationID FROM station WHERE Disziplin='" + discipline + "';").fetchall()
            if len(res) == 0:
                return "error"
            for s in res:
                stationen.append(int(s[0]))
            # if Station in [] --> continue else add String
            ret = ""
            for result in results:
                klassen = dbCur.execute("SELECT Name FROM klasse WHERE Klassenstufe=" + str(result[0])).fetchall()
                if len(klassen) == 0:
                    continue
                for k in klassen:
                    for s in stationen:
                        if len(dbCur.execute("SELECT status FROM zuweisungStation WHERE StationID=" + str(s) + " AND klasse='" + k[0] + "'").fetchall()) != 0:
                            continue
                        ret += k[0] + "\n"
            return ret

@app.route('/station/getDetails')
def get_details():
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else:
        stationID = request.args.get('id')
        dbCon, dbCur = _server.getDB()
        results = dbCur.execute("SELECT Name,Lehrer,Disziplin FROM station WHERE StationID=" + stationID).fetchall()
        if len(results) != 1:
            return "error"
        result = results[0]
        disziplin = result[2]
        name = result[0]
        lehrerkürzel = result[1]
        # cn, vorname, nachname, loginName, anzeigeName
        user = _server._ldapU.getUserDetail(lehrerkürzel)
        vorname = user[1][0].decode("utf-8")
        nachname = user[2][0].decode('utf-8')
        ret = "" + name + "\n" + disziplin + "\n" + lehrerkürzel + "\n" + vorname + " " + nachname
        dbCon.close()
        return ret

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
        stationID = request.args.get('id')
        dbCon, dbCur = _server.getDB()
        if stationID != "-1":
            results = dbCur.execute("SELECT Lehrer FROM station WHERE StationID=" + request.args.get('id')).fetchall()
            if len(results) != 1:
                return "error"
            lehrerStation = results[0][0]
        alleLehrer = _server._ldapU.getAllGroupMembers(_server._cnUserGruppe)
        print(alleLehrer)
        results = dbCur.execute("SELECT Lehrer FROM station").fetchall()
        ret = ""
        for r in results:
            if r[0] in alleLehrer:
                alleLehrer.remove(r[0])
        if stationID != "-1":
            alleLehrer.append(lehrerStation)
        for lehrer in alleLehrer:
            # cn, vorname, nachname, loginName, anzeigeName
            user = _server._ldapU.getUserDetail(lehrer)
            vorname = user[1][0].decode("utf-8")
            nachname = user[2][0].decode("utf-8")
            ret += lehrer + ";" + vorname + " " + nachname + "\n"
        dbCon.close()
        return ret

@app.route('/station/changeData', methods=["POST"])
def change_data():
    if not checkAdmin():
        return "error"
    if request.method == "POST":
        lehrer = request.form["lehrer"]
        name = request.form["name"]
        stationID = request.form["id"]
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("UPDATE station SET lehrer='" + lehrer + "', Name='" + name + "' WHERE StationID=" + stationID)
            dbCon.commit()
            dbCon.close()
        except:
            return "error"
        return "success"

@app.route('/station/addClass', methods=["POST"])
def add_class_station():
    if not checkAdmin():
        return "error"
    if request.method == "POST":
        klasse = request.form["class"]
        stationID = request.form["id"]
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("INSERT INTO zuweisungStation (StationID, Klasse) VALUES (" + stationID + ",'" + klasse + "')")
            dbCon.commit()
            dbCon.close()
        except:
            return "error"
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
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("DELETE FROM zuweisungStation WHERE StationID=" + stationID + " AND Klasse='" + klasse + "'")
            dbCon.commit()
            dbCon.close()
        except:
            return "error"
        return "success"

@app.route('/station/deleteStation')
def delete_station():
    if not checkAdmin():
        return "error"

    if request.args.get('id') == None:
        return "error"
    else:
        stationID = request.args.get('id')
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("DELETE FROM zuweisungStation WHERE StationID=" + stationID)
            dbCur.execute("DELETE FROM wert WHERE StationID=" + stationID)
            dbCur.execute("DELETE FROM station WHERE StationID=" + stationID)
            dbCon.commit()
            dbCon.close()
        except:
            return "error"
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
        try:
            dbCon, dbCur = _server.getDB()
            dbCur.execute("INSERT INTO station (Lehrer, Disziplin, Name) VALUES ('" + teacher + "','" + discipline + "','" + name + "');")
            dbCon.commit()
            dbCon.close()
        except:
            return "error"
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

@app.route('/students/upload', methods=["POST"])
def upload_students():
    if not checkAdmin():
        return "error"
    if request.method == "POST":
        if 'csv-file' not in request.files:
            return "error"
        file = request.files["csv-file"]
        if file.filename == "":
            return "error"
        if file:
            csv = file.read().decode('utf-8')
            print(csv)
            #'Schuelernummer','Jahrgang','Klasse','Geschlecht', Fahrschüler(unnötig),'Name','Vorname', 'Geburtsdatum'
            students = csv.split("\n")
            dbCon, dbCur = _server.getDB()
            for s in students:
                if s == "":
                    continue
                infos = s.split(";")
                if len(dbCur.execute("SELECT Klasse FROM schueler WHERE SchuelerNr=" + infos[0]).fetchall()) != 0:
                    continue
                if len(dbCur.execute("SELECT Klassenstufe FROM Klasse WHERE Name='" + infos[2] + "'").fetchall()) == 0:
                    klassenstufe = re.findall("\d+", infos[2])[0]
                    dbCur.execute('INSERT INTO klasse (Name,Klassenstufe) VALUES ("' + infos[2] + '",' + klassenstufe + ');')
                    dbCon.commit()
                dbCur.execute("INSERT INTO schueler (SchuelerNr,Jahrgang, Klasse, Geschlecht,Name,Vorname,Geburtsdatum) VALUES(" + infos[0] + "," + infos[1] + ",'" + infos[2] + "','" + infos[3] + "','" + infos[5] + "','" + infos[6] + "','" + infos[7] + "');")
                dbCon.commit()
            dbCon.close()
        else:
            return "error"
        return "success"

@app.route('/settings/getCurrent')
def get_current_settings():
    if not checkAdmin():
        return "error"
    _server.ladeEinstellungen()
    ret = _server._adAdminUser + ";" + _server._adServer + ";" + _server._cnAdminGruppe + ";" + _server._cnUserGruppe + ";" + _server._adBaseDN
    return ret

@app.route('/settings/changeGeneral', methods=["POST"])
def change_general_settings():
    if not checkAdmin():
        return "error;Permission denied"
    if request.method == "POST":
        if request.form["adUsername"] == None or request.form["adPassword"] == None or request.form["adServer"] == None \
            or request.form["cnAdminGroup"] == None or request.form["cnUserGroup"] == None:
            return "error;API-Request incomplete"
        adUsername = request.form["adUsername"]
        adPassword = request.form["adPassword"]
        adServer = request.form["adServer"]
        cnAdminGruppe = request.form["cnAdminGroup"]
        cnUserGruppe = request.form["cnUserGroup"]
        print(adUsername + " " + adPassword + " " + adServer + " " + cnAdminGruppe + " " + cnUserGruppe)

        basedn = ""
        try:
            domain = adUsername.split("@")[1]
        except:
            return "error;Username does not include Domain name"

        if domain == "":
            return "error;Username does not include Domain name"
        dn = domain.split(".")
        for d in dn:                    
            basedn += "DC=" + d + ","
        basedn = basedn[:-1]
        print(basedn)
        domain = "@" + domain
        print(domain)

        try:
            conn = ldap.initialize('ldap://' + adServer)
            conn.protocol_version = 3
            conn.set_option(ldap.OPT_REFERRALS, 0)
        except:
            print("Server Error")
            return "error;Server Error"

        try:
            result = conn.simple_bind_s(adUsername, adPassword)
        except ldap.INVALID_CREDENTIALS:
            return "error;Permission on Server denied - Maybe wrong password or username"
        except ldap.SERVER_DOWN:
            return "error;Server down"
        except ldap.LDAPError:
            return "error;Other LDAP error"

        try:
            result = conn.search_s(basedn, ldap.SCOPE_SUBTREE, "(&(objectClass=GROUP)(cn=" + cnAdminGruppe + "))")
        except:
            return "error;Error admin group"
        if result:
            if len(result[0]) >= 2 and 'member' in result[0][1]:
                members_tmp = result[0][1]['member']
                if len(members_tmp) == 0:
                    return "error;No user in admingroup or wrong name"
            else:
                return "error;No user in admingroup or wrong name"

        result = conn.search_s(basedn, ldap.SCOPE_SUBTREE, "(&(objectClass=GROUP)(cn=" + cnUserGruppe + "))")
        if result:
            if len(result[0]) >= 2 and 'member' in result[0][1]:
                members_tmp = result[0][1]['member']
                if len(members_tmp) == 0:
                    return "error;No user in usergroup or wrong name"
            else:
                return "error;No user in usergroup or wrong name"
        dbCon, dbCur = _server.getDB()
        try:
            dbCur.execute("UPDATE einstellung SET Wert='" + cnAdminGruppe + "' WHERE Name='cnAdminGruppe'")
            dbCur.execute("UPDATE einstellung SET Wert='" + cnUserGruppe + "' WHERE Name='cnUserGruppe'")
            dbCur.execute("UPDATE einstellung SET Wert='" + adServer + "' WHERE Name='adServer'")
            dbCur.execute("UPDATE einstellung SET Wert='" + adPassword + "' WHERE Name='adPasswort'")
            dbCur.execute("UPDATE einstellung SET Wert='" + basedn + "' WHERE Name='adBaseDN'")
            dbCur.execute("UPDATE einstellung SET Wert='" + domain + "' WHERE Name='domainName'")
            dbCur.execute("UPDATE einstellung SET Wert='" + adUsername + "' WHERE Name='adAdminUser'")
        except:
            return "error;DB-Error"
        dbCon.commit()
        dbCon.close()
        return "success;"

@app.route('/settings/deleteAllData')
def method_name():
    if not checkAdmin():
        return "error"
    else:
        dbCon, dbCur = _server.getDB()
        try:
            dbCur.execute("DELETE FROM disziplin")
            dbCur.execute("DELETE FROM klasse")
            dbCur.execute("DELETE FROM schueler")
            dbCur.execute("DELETE FROM station")
            dbCur.execute("DELETE FROM wert")
            dbCur.execute("DELETE FROM zuweisungStation")
            dbCur.execute("DELETE FROM sqlite_sequence")
        except:
            return "error;DB-Error"
        dbCon.commit()
        dbCon.close()

        return "success"

if __name__ == "__main__":
    _server = Server()
    app.run(host="0.0.0.0", debug=True)