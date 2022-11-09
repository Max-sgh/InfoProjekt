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
        

        self._zuschlag = 0.24

    def berechnePunkte(self, wert, geschlecht, messung, distanz) -> int:
        punkte = 0
        if messung == 'h':
            if geschlecht == 'm' and distanz == 50:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aM50) / self.cM50
            if geschlecht == 'w' and distanz == 50:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aW50) / self.cW50

            if geschlecht == 'm' and distanz == 75:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aM75) / self.cM75
            if geschlecht == 'w' and distanz == 75:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aW75) / self.cW75

            if geschlecht == 'm' and distanz == 100:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aM100) / self.cM100
            if geschlecht == 'w' and distanz == 100:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aW100) / self.cW100

        if messung == 'e':
            if geschlecht == 'm' and distanz == 50:
                punkte = ((distanz / (wert)) - self.aM50) / self.cM50
            if geschlecht == 'w' and distanz == 50:
                punkte = ((distanz / (wert)) - self.aW50) / self.cW50

            if geschlecht == 'm' and distanz == 75:
                punkte = ((distanz / (wert)) - self.aM75) / self.cM75
            if geschlecht == 'w' and distanz == 75:
                punkte = ((distanz / (wert)) - self.aW75) / self.cW75

            if geschlecht == 'm' and distanz == 100:
                punkte = ((distanz / (wert)) - self.aM100) / self.cM100
            if geschlecht == 'w' and distanz == 100:
                punkte = ((distanz / (wert)) - self.aW100) / self.cW100

        if punkte < 0:
            punkte = 0
            
        return math.floor(punkte)