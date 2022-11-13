import math
from disziplin import Disziplin

class Laufen(Disziplin):
    def __init__(self):
        self.aW800 = 2.02320
        self.cW800 = 0.00647
        self.aW2000 = 1.80000
        self.cW2000 = 0.00540
        self.aW3000 = 1.75000
        self.cW3000 = 0.00500

        self.aM800 = 2.32500
        self.cM800 = 0.00644
        self.aM1000 = 2.15800
        self.cM1000 = 0.00600
        self.aM2000 = 1.78400
        self.cM2000 = 0.00600
        self.aM3000 = 1.70000
        self.cM3000 = 0.00580

        self._zuschlag = 0

    def berechnePunkte(self, wert, geschlecht, messung, distanz) -> int:
        punkte = 0
        if messung == 'h':
            if geschlecht == 'm' and distanz == 800:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aM800) / self.cM800
            if geschlecht == 'w' and distanz == 800:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aW800) / self.cW800

            if geschlecht == 'm' and distanz == 1000:
                punkte = ((distanz / (wert)) - self.aM1000) / self.cM1000
            if geschlecht == 'w' and distanz == 1000:
                punkte = ((distanz / (wert)) - self.aW1000) / self.cW1000

            if geschlecht == 'm' and distanz == 2000:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aM2000) / self.cM2000
            if geschlecht == 'w' and distanz == 2000:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aW2000) / self.cW2000
                
            if geschlecht == 'm' and distanz == 3000:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aM3000) / self.cM3000
            if geschlecht == 'w' and distanz == 3000:
                punkte = ((distanz / (wert+self._zuschlag)) - self.aW3000) / self.cW3000

        if messung == 'e':
            if geschlecht == 'm' and distanz == 800:
                punkte = ((distanz / (wert)) - self.aM800) / self.cM800
            if geschlecht == 'w' and distanz == 800:
                punkte = ((distanz / (wert)) - self.aW800) / self.cW800

            if geschlecht == 'm' and distanz == 1000:
                punkte = ((distanz / (wert)) - self.aM1000) / self.cM1000

            if geschlecht == 'm' and distanz == 2000:
                punkte = ((distanz / (wert)) - self.aM2000) / self.cM2000
            if geschlecht == 'w' and distanz == 2000:
                punkte = ((distanz / (wert)) - self.aW2000) / self.cW2000

            if geschlecht == 'm' and distanz == 3000:
                punkte = ((distanz / (wert)) - self.aM3000) / self.cM3000
            if geschlecht == 'w' and distanz == 3000:
                punkte = ((distanz / (wert)) - self.aW3000) / self.cW3000

        if punkte < 0:
            punkte = 0
            
        return math.floor(punkte)