class Schueler {
    vorname;
    nachname;
    schuelerNr;
    inpWert;

    constructor(vorname, nachname, schuelerNr) {
        this.vorname = vorname;
        this.nachname = nachname;
        this.schuelerNr = schuelerNr;
    }

    sendeWert(wert) {
        //wert = inpWert.value;
        console.log(this.vorname + " " + this.nachname + " - " + this.schuelerNr + ": " + wert);
    }
}