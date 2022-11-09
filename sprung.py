import math
from disziplin import Disziplin

class Sprung(Disziplin):
    def __init__(self):
        self.aWHoch = 0.88070
        self.cWHoch = 0.00068
        self.aWWeit = 1.09350
        self.cWWeit = 0.00208
        
        self.aMHoch = 0.84100
        self.cMHoch = 0.00080
        self.aMWeit = 1.15028
        self.cMWeit = 0.00219
        

        self._zuschlag = 0

    def berechnePunkte(self, wert, geschlecht, art) -> int:
        punkte = 0
        if geschlecht == 'm' and art == "hochsprung":
            punkte = ((math.sqrt(wert) - self.aMHoch) / self.cMHoch)
        if geschlecht == 'w' and art == "hochsprung":
            punkte = ((math.sqrt(wert) - self.aWHoch) / self.cWHoch)
        if geschlecht == 'm' and art == "weitsprung":
            punkte = ((math.sqrt(wert) - self.aMWeit) / self.cMWeit)
        if geschlecht == 'w' and art == "weitsprung":
            punkte = ((math.sqrt(wert) - self.aWWeit) / self.cWWeit)
            
        if punkte < 0:
            punkte = 0
            
        return math.floor(punkte)
        