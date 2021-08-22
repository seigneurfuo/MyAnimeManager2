import os


def python_version():
    """Retourne vrai si la version de python est 2.x"""

    from sys import version_info
    return version_info[0]


def open_file_explorer(path):
    """Ouvre un explorateur de fichiers à l'adresse indiquée en argument"""

    import platform

    try:
        if platform.system() == "Windows":
            from os import startfile
            startfile(path)

        elif platform.system() == "Darwin":
            from subprocess import Popen
            Popen(["open", path])

        else:
            from subprocess import Popen
            Popen(["xdg-open", path])

    except:
        return None


def href_link(text):
    if text:
        return "<a href=\"{text}\">{text}</a".format(text=text)
    else:
        return ""


def get_serie_cover(appDir, appDataFolder, serie_id):
    cover_filename = os.path.join(appDataFolder, "covers/{0}".format(serie_id))
    if not os.path.isfile(cover_filename):
       cover_filename = os.path.join(appDir, "ressources/icons/image-x-generic.png")

    return cover_filename