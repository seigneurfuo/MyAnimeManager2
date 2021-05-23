# https://sysgenre.it/automatisation-de-template-docx/

from database import *
import docxtpl


def generate_series_list(template_file, output_file):
    series = Serie.select().where(Serie.serie_sort_id != 0).order_by(Serie.serie_sort_id.desc())
    
    line_break = docxtpl.RichText("\n")
    data = {
        "document_title": "Liste des animés", 
        "series": series, 
        "line_break": line_break
    }

    document = docxtpl.DocxTemplate(template_file)
    document.render(data)
    document.save(output_file)


def generate_planning(template_file, output_file):
    dates = Planning.select().order_by(Planning.planning_date.desc())
    
    line_break = docxtpl.RichText("\n")
    data = {
        "document_title": "Planning des séries", 
        "dates": dates, 
        "line_break": line_break
    }

    document = docxtpl.DocxTemplate(template_file)
    document.render(data)
    document.save(output_file)


def main():
    generate_series_list("template_liste.docx", "Liste des animés.docx")
    #generate_planning("template_planning.docx", "Planning de visonnage.docx")


main()