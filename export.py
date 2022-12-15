from fpdf import FPDF
from datetime import date

class PdfExport(object):
    def __init__(self) -> None:
        self.pdf = FPDF(orientation="L", format="A4", unit="pt")
    
    def exportClass(self, data, name, disciplines) -> FPDF:
        # A4: 842 pt x 595 pt
        self.pdf.add_page()
        self.pdf.set_font("arial", "B", 14)
        self.pdf.cell(700, 20, "Leistungsübersicht Sportfest " + str(date.today().year) + " | Klasse " + name, "B", 0)
        self.pdf.cell(100, 20, date.today().strftime("%d.%m.%Y"), "B", 2, "R")
        self.pdf.ln(10)

        self.pdf.set_font("arial", "B", size=8)
        self.pdf.set_fill_color(33,37,41)
        self.pdf.set_text_color(255,255,255)
        self.pdf.cell(55,15, "SchülerNr", fill=True)
        self.pdf.cell(137,15, "Name", fill=True)
        self.pdf.cell(137,15, "Vorname", fill=True)
        #dis = ["Sprint (50m)", "Laufen (1000m)"]
        sizes = []
        for d in disciplines:
            self.pdf.cell(self.pdf.get_string_width(d)+10,15, d, fill=True)
            sizes.append(self.pdf.get_string_width(d)+10)
        self.pdf.ln()
        self.pdf.set_font("arial", "", size=8)
        for i in range(len(data)):
            schueler = data[i]
            if i % 2 == 0:
                self.pdf.set_fill_color(204,204,204)
            else:
                self.pdf.set_fill_color(238,238,238)
            self.pdf.set_text_color(0,0,0)
            self.pdf.cell(55, 15, schueler[0], fill=True)
            self.pdf.cell(137, 15, schueler[1], fill=True)
            self.pdf.cell(137, 15, schueler[2], fill=True)
            j = 0
            for k in range(len(schueler) - 3):
                self.pdf.cell(sizes[j], 15, schueler[k + 3], fill=True)
                j += 1
            self.pdf.ln()
        return self.pdf

    def exportGradeLevel(self, data, names, disciplines) -> FPDF:
        for i in range(len(data)):
            print(data[i], names[i])
            #self.pdf.add_page()
            self.exportClass(data[i], names[i], disciplines)
        return self.pdf


#pdf = PdfExport()
#export = pdf.exportClass([["15073", "Lange", "Maximilian", "13,5s", "5:38min"], ["15709", "Georg", "DomDom", "9,8s", "3:08min"], ["18752", "Möller", "Maurice", "5,28s", "3:24min"]], "10b")
#export.output("test.pdf")
#export = pdf.exportGradeLevel([[["15073", "Lange", "Maximilian", "13,5s", "5:38min"]], [["15709", "Georg", "DomDom", "9,8s", "3:08min"], ["18752", "Möller", "Maurice", "5,28s", "3:24min"]]], ["10b", "8a"], ["Sprint (50m)", "Laufen (1000m)"])
#export.output("test.pdf")