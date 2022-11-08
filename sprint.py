import math
from disziplin import Disziplin

class Sprint(Disziplin):
    def __init__(self):
        self.aW50 = 3.648
        self.cW50 = 0.0066
        self.aW75 = 3.998
        self.cW75 = 0.0066
        self.aW100 = 4.0062
        self.cW100 = 0.00656

        self.aM50 = 3.79
        self.cM50 = 0.0069
        self.aM75 = 4.1
        self.cM75 = 0.00664
        self.aM100 = 4.341
        self.cM100 = 0.00676

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