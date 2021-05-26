# https://sysgenre.it/automatisation-de-template-docx/

from database import *
import docxtpl


def generate_series_list(template_file, output_file):
    series = Serie.select() \
        .where(Serie.serie_sort_id != 0) \
        .order_by(Serie.serie_sort_id \
        .desc())

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
    dates = Planning.select() \
        .join(Serie, on=(Planning.planning_fk_serie == Serie.serie_id)) \
        .join(Season, on=(Planning.planning_fk_season == Season.season_id)) \
        .order_by(Planning.planning_date \
        .desc(), Planning.planning_fk_serie.serie_sort_id, Planning.planning_fk_season.season_sort_id, Planning.planning_episode_id)
    
    line_break = docxtpl.RichText("\n")
    data = {
        "document_title": "Planning des séries", 
        "dates": dates, 
        "line_break": line_break
    }

    output_file = output_file.replace(".docx", ".txt")
    with open(output_file, "w") as output_file_writer:
        for date in dates:
            row = "{} - {} - {} - {}".format(date.planning_date, date.planning_fk_serie.serie_title, date.planning_fk_season.season_title, date.planning_episode_id)

            output_file_writer.write(row + "\n")

    msg = "Nombre de lignes multiples dans le planning: {} sur {} lignes exportées !".format(already_exists_count, len(dates))
    print(msg)

    #document = docxtpl.DocxTemplate(template_file)
    #document.render(data)
    #document.save(output_file)


def main():
    #generate_series_list("template_liste.docx", "Liste des animés.docx")
    generate_planning("template_planning.docx", "Planning de visionnage.docx")


main()