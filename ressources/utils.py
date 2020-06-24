def python2():
    """Retourne vrai si la version de python est 2.x"""

    from sys import version_info
    return version_info[0] == 2


def open_filebrowser(path):
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
