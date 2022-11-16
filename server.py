from sprint import Sprint
from laufen import Laufen
from sprung import Sprung
from wurf import Werfen
from ldapUtils import ldapUtils
import sqlite3


class Server(object):
    def __init__(self):
        self.ladeEinstellungen()
        self._ldapU = ldapUtils(self._adBaseDN, self._adServer, self._adAdminUser, self._adPasswort)
    
    def ladeEinstellungen(self):
        dbCon, dbCur = self.getDB()
        results = dbCur.execute("SELECT Name, Wert FROM einstellung").fetchall()
        if len(results) == 0:
            return ""
        for r in results:
            name = r[0]
            wert = r[1]
            if name == "cnAdminGruppe":
                self._cnAdminGruppe = wert
            if name == "cnUserGruppe":
                self._cnUserGruppe = wert
            if name == "adBaseDN":
                self._adBaseDN = wert
            if name == "domainName":
                self._domainName = wert
            if name == "adServer":
                self._adServer = wert
            if name == "adAdminUser":
                self._adAdminUser = wert
            if name == "adPasswort":
                self._adPasswort = wert
        """self._cnUserGruppe = "Lehrer"
        #_adBaseDN = "DC=gymsgh,DC=local"
        self._adBaseDN = "DC=srv-lange,DC=de"
        #_domainName = "@gymsgh.local"
        self._domainName = "@srv-lange.de"
        #_adServer = "172.20.0.2"
        self._adServer = "192.168.178.54"
        self._adAdminUser = "Administrator@srv-lange.de" #"admin@gymsgh.local" #"admin"
        self._adPasswort = "Rsu3sc123" #"12345" """

    
    def getDB(self):
        dbCon = sqlite3.connect("sportfest.db")
        dbCur = dbCon.cursor()
        return dbCon, dbCur

    def berechnePunkte(self, stationID, wert, schuelerNr) -> int:
        punkte = 0
        #
        # Disziplin über stationID ermitteln und fehlende Werte ergänzen
        #
        dbCon, dbCur = self.getDB()
        results = dbCur.execute("SELECT Disziplin FROM station WHERE stationID=" + str(stationID)).fetchall()
        if len(results) != 1:
            print("Error 1")
            return ""
        disziplin = results[0][0]
        results = dbCur.execute("SELECT Geschlecht,Klasse FROM schueler WHERE SchuelerNr='" + str(schuelerNr) + "';").fetchall()
        if len(results) != 1:
            print("Error 2")
            return ""
        geschlecht = results[0][0]
        klasse = results[0][1]
        results = dbCur.execute("SELECT Klassenstufe FROM klasse WHERE Name='" + klasse + "'").fetchall()
        if len(results) != 1:
            print("Error 3")
            return ""
        klassenstufe = results[0][0]
        results = dbCur.execute("SELECT Messung FROM disziplin WHERE Klassenstufe=" + str(klassenstufe) + " AND Disziplin='" + disziplin + "';").fetchall()
        if len(results) != 1:
            print("Error 4")
            return ""
        messung = results[0][0]

        if disziplin.startswith('sprint'):
            wert = float(wert)
            distanz = int(disziplin.split('sprint')[1])
            punkte = Sprint().berechnePunkte(wert, geschlecht, messung, distanz)
        if  disziplin.startswith('laufen'):

            distanz = str(disziplin.split('laufen')[1])
            punkte = Laufen().berechnePunkte(wert, geschlecht, distanz)
        if  disziplin.startswith('ballwurf') or disziplin == "kugelstoss" or disziplin == "schleuderball":
            wert = float(wert)
            punkte = Werfen().berechnePunkte(wert, geschlecht, disziplin)
        if disziplin == "hochsprung" or disziplin == "weitsprung":
            wert = float(wert)
            punkte = Sprung().berechnePunkte(wert, geschlecht, disziplin)
        return punkte
