#!/bin/python

# seigneurfuo - http://github.com/seigneurfuo
# Date de création: 10/07/2017
# Dernière modification: 29/04/2017

#
# Un gestionnaire de séries basé sur le code de MyAnimeManager
#

# Informations de l'application
__version__ = "2019.01.14-BETA"

import sys
from ressources.utils import python2

# Vérification de la version de Python minimale pour lancer
if python2(): sys.exit('Cette application à besoin de Python 3 pour fonctionner ! Veuillez l\'installer au préalable: http://python.org/download')


from PyQt5.QtWidgets import QApplication
from ressources.MainWindow import MainWindow
from os.path import dirname

def main():
    """Fonction principale"""

    appDir = dirname(__file__)
    print("MyAnimeManager - Version:", __version__, appDir)

    app = QApplication(sys.argv)
    mainwindow = MainWindow(__version__, appDir)
    sys.exit(app.exec_())


main()
