#!/bin/env python3

# seigneurfuo - http://github.com/seigneurfuo
# Date de création: 10/07/2017
# Dernière modification: 20/10/2017

#
# Un gestionnaire de séries basé sur le code de MyAnimeManager
#

# Informations de l'application
__version__ = "2021.08.22"

import sys
from ressources.utils import python_version

# Vérification de la version de Python minimale pour lancer
if python_version() == 2:
    sys.exit('Cette application à besoin de Python 3 pour fonctionner ! Veuillez l\'installer au préalable: https://python.org/download')

from PyQt5.QtWidgets import QApplication
from ressources.MainWindow import MainWindow
from os.path import dirname


def main():
    """Fonction principale"""

    app_dir = dirname(__file__)
    print("MyAnimeManager - Version:", __version__, app_dir)

    app = QApplication(sys.argv)
    mainwindow = MainWindow(__version__, app_dir)
    mainwindow.show()
    sys.exit(app.exec_())


main()
