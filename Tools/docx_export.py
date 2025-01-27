# https://sysgenre.it/automatisation-de-template-docx/
from datetime import datetime

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
        .order_by(Planning.planning_date.desc(),
                  Planning.planning_fk_serie.serie_sort_id, Planning.planning_fk_season.season_sort_id,
                  Planning.planning_episode_id.desc())

    line_break = docxtpl.RichText("\n")
    data = {
        "document_title": "Planning des séries",
        "dates": dates,
        "line_break": line_break
    }

    # Variables pour les saut de lignes (permet de fait des groupes)
    old_year = None
    old_month = None

    output_file = output_file.replace(".docx", ".txt")
    with open(output_file, "w") as output_file_writer:
        for date in dates:
            # On ajoute des lignes spéciales
            year = date.planning_date.strftime("%Y")
            month = date.planning_date.strftime("%m")

            if old_year and (year != old_year):
                msg = "\n" + "----- " * 5 + year + "----- " * 5 + "\n\n"
                output_file_writer.write(msg)
                print("\n", year)

            elif old_month and (month != old_month):
                output_file_writer.write("\n")

                print("  ", month)

            old_year = year
            old_month = month

            # On écrit la ligne normale
            row = "{} - {} - {} - {}".format(date.planning_date, date.planning_fk_serie.serie_title,
                                             date.planning_fk_season.season_title, date.planning_episode_id)
            output_file_writer.write(row + "\n")

    msg = "Nombre de lignes lignes exportées: {}.".format(len(dates))
    print(msg)

    # document = docxtpl.DocxTemplate(template_file)
    # document.render(data)
    # document.save(output_file)


def main():
    # generate_series_list("Templates/template_liste.docx", "Liste des animés.docx")
    generate_planning("Templates/template_planning.docx", "Planning de visionnage.docx")


main()
