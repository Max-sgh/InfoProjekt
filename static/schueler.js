class Schueler {
    vorname;
    nachname;
    schuelerNr;
    inpWert;
    klasse;
    punkteGesamt;
    geschlecht;

    constructor(vorname, nachname, schuelerNr) {
        this.vorname = vorname;
        this.nachname = nachname;
        this.schuelerNr = schuelerNr;
    }
    
    /*createSchueler(schuelerNr, vorname, nachname, klasse, geschlecht, punkte) {
        this.vorname = vorname;
        this.nachname = nachname;
        this.schuelerNr = schuelerNr;
        this.klasse = klasse;
        this.punkteGesamt = punkte;
        this.geschlecht = geschlecht;
    }*/

    sendeWert(wert) {
        //wert = inpWert.value;
        console.log(this.vorname + " " + this.nachname + " - " + this.schuelerNr + ": " + wert);
    }
}