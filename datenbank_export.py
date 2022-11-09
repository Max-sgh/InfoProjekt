from csv import *
from lib2to3.pgen2.token import STRING
from msvcrt import kbhit
from pickle import TRUE
from sqlite3 import *


#app = Flask(__name__, static_folder="static")

schueler=[]





def csv(schueler1):
    schueler1=('Schuelernummer','Jahrgang','Klasse','Geschlecht','Name','Vorname', 'Geburtsdatum')

def array1():
    i=0
    j=0
    csv1=[j]
    k=""
    STRING[i]=("C:\Benutzer\15080\Desktop\test.csv")
     
    while (j==5):
        j=j+1

    while (STRING[i]==';'):
        i=i+1
        csv1[j] = k
        k =""
        j =j+1

        else:
            k = k+ STRING[i]
            i=i+1
    print(csv1)

array1()


