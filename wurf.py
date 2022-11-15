import math
from disziplin import Disziplin

class Werfen (Disziplin):
    def __init__(self):
        self.aWKugel = 1.27900
        self.cWKugel = 0.00398
        self.aWSchleuder = 1.08500
        self.cWSchleuder = 0.00921
        self.aW200 = 1.41490
        self.cW200 = 0.01039
        self.aW80 = 2.02320	
        self.cW80 = 0.00874

        self.aMKugel = 1.27900
        self.cMKugel = 0.00398
        self.aMSchleuder = 1.08500
        self.cMSchleuder = 0.00921
        self.aM200 = 1.41490
        self.cM200 = 0.01039
        self.aM80 = 2.02320	
        self.cM80 = 0.00874


        self._zuschlag = 0

    def berechnePunkte(self, wert, geschlecht, art) -> int:
        punkte = 0
        if geschlecht == 'm' and art == "kugelstoss":
            punkte = ((math.sqrt(wert) - self.aMKugel) / self.cMKugel)
        if geschlecht == 'w' and art == "kugelstoss":
            punkte = ((math.sqrt(wert) - self.aWKugel) / self.cWKugel)
        if geschlecht == 'm' and art == "schleuderball":
            punkte = ((math.sqrt(wert) - self.aMSchleuder) / self.cMSchleuder)
        if geschlecht == 'w' and art == "schleuderball":
            punkte = ((math.sqrt(wert) - self.aWSchleuder) / self.cWSchleuder)
        if geschlecht == 'm' and art == "ballwurf200":
            punkte = ((math.sqrt(wert) - self.aM200) / self.cM200)
        if geschlecht == 'w' and art == "ballwurf200":
            punkte = ((math.sqrt(wert) - self.aW200) / self.cW200)
        if geschlecht == 'm' and art == "ballwurf80":
            punkte = ((math.sqrt(wert) - self.aM80) / self.cM80)
        if geschlecht == 'w' and art == "ballwurf80":
            punkte = ((math.sqrt(wert) - self.aW80) / self.cW80)

        if punkte < 0:
            punkte = 0
            
        return math.floor(punkte)
        

