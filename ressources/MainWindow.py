from PyQt5.QtCore import QTime, Qt, QDate, QRect
from PyQt5.QtGui import QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QMessageBox, QListWidgetItem, QMainWindow, QTableWidgetItem, QAbstractScrollArea, \
    QProgressBar
from PyQt5.uic import loadUi

# Modales
from ressources.SeasonModal import SeasonModal
from ressources.SerieModal import SerieModal

# Tables SQL
from ressources.sql import *

import os
import sqlite3
from json import load, dump
from datetime import datetime, timedelta
from pathlib import Path
from random import randint

# Modules locaux
from ressources.ressource import icons # Chemins vers les fichiers (TODO: à remplacer dans le futur par un qrc)
from ressources.log import *
from ressources.utils import *
from ressources.calendar import Calendar


class MainWindow(QMainWindow):
    """Classe de la fenetre princinpale"""

    def __init__(self, version, appDir):
        """

        :param version: La version de l'application (uniquement pour afficher le titre et
        :param appDir:
        """

        super(MainWindow, self).__init__()

        # Répertoire de travail de l'application lancée
        self.appDir = appDir

        self.defaultSettings = {"startupPageId": 1, "realtimeSearch": False}
        self.settings = {}

        self.seriesList = []
        self.seriePath = ""
        self.currentSerieId = 0

        self.seasonsList = []
        self.currentSeasonId = 0
        self.seasonStates = ["Indéfinie", "A voir", "En cours", "Terminée"]
        self.seasonLanguages = ["Indéfinie", "Japonais", "Japonais & Francais (Dual Audio)", "Français", "Autres"]

        self.planningWatched = []
        self.planningToWatch = []

        # Indique si les modifications on eté sauvegardées (permet d'afficher un message uniquement si il y a des informations à sauvegarder)
        self.unsaved = False

        # Création du profil
        self.profile__create()

        # Vérification / Création de la base de données
        self.database_()

        # Initialise l'affichage
        self.setup_Ui(version)

        # Chargement des paramètres
        self.settings__load()

        # Chargement des évenements des élements de l'interface
        self.events()

        # Chargement des evenement par rapport à l'onglet
        self.on_tab_changed()

        # Définition du premier onglet affiché (ici car c'est un parametre qui n'est utilisé qu'au démarrage
        self.tabWidget.setCurrentIndex(self.settings["startupPageId"])

        # Affichage de la fenètre
        self.show()


    def setup_Ui(self, version):
        """

        :param version: Version de l'application
        :return: None
        """

        loadUi(os.path.join(self.appDir, 'ressources/MainWindow.ui'), self)

        # Chargement du calendrier personalisé
        self.planningCalendar = Calendar()
        self.planningCalendar.setCellsBackgroundColor(QColor(115, 210, 22, 50))
        self.verticalLayout_3.addWidget(self.planningCalendar)

        windowTitle = "MyAnimeManager2 - version {0}".format(version)
        self.setWindowTitle(windowTitle)


    def events(self):
        """Définition de tout les évènements de la fenetre pricipale"""

        # Evenement de changement des onglets
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Evenement de fermeture de la fenetre
        self.closeEvent = self.on_close

        # ----- Onglet Planning -----
        self.planningCalendar.clicked.connect(self.planningtab__watched__fill)
        self.pushButton_9.clicked.connect(self.planningtab__calendar__today)
        self.planningAddButton.clicked.connect(self.planningtab__watched__add)
        # self.tableWidget_3.cellClicked.connect(self.planningtab__watched__add)
        self.tableWidget_3.currentCellChanged.connect(self.planningtab__is_button_need_to_be_enabled)

        self.pushButton_13.clicked.connect(self.planningtab__open_explorer)  # Ouverture du dossier de la série
        self.checkBox.clicked.connect(self.planningtab__next__fill)
        self.planningDeleteButton.clicked.connect(self.planningtab__watched__remove)

        # ----- Onglet liste -----
        self.pushButton.clicked.connect(self.listtab__create_serie)  # Création série
        self.pushButton_3.clicked.connect(self.listtab__edit_serie)  # Edition série
        self.pushButton_2.clicked.connect(self.listtab__delete_serie)  # Suppression série
        self.randomSerieButton.clicked.connect(self.listtab__random_serie)
        self.pushButton_10.clicked.connect(self.listtab__open_explorer)  # Ouverture du dossier de la série

        self.pushButton_5.clicked.connect(self.listtab__create_season)  # Création saison
        self.pushButton_4.clicked.connect(self.listtab__edit_season)  # Edition saison
        self.pushButton_6.clicked.connect(self.listtab__delete__season)  # Suppression saison

        self.lineEdit.returnPressed.connect(self.listtab__serieslist__search)  # Barre de recherche de série
        if self.settings["realtimeSearch"]:
            self.lineEdit.textChanged.connect(self.listtab__serieslist__search)  # Barre de recherche de série (recherche en direct)

        self.pushButton_14.clicked.connect(self.listtab__serieslist__search_clear)  # Bouton de nettoyage de la liste

        # Evenement des listes de sélections (séries et saisons)
        self.comboBox_2.currentIndexChanged.connect(self.listtab__series__changed)
        self.comboBox.currentIndexChanged.connect(self.listtab__seasons__changed)

        # ----- Onglet outils -----
        self.pushButton_7.clicked.connect(self.tools__watch_time__execute)
        self.pushButton_8.clicked.connect(self.tools__watch_time__local_time)

        # ----- Onglet notes -----
        self.pushButton_12.clicked.connect(self.notestab__save)

        # ----- Onglet paramètres -----
        self.pushButton_11.clicked.connect(self.settings__save)


    def on_tab_changed(self):
        """Fonction déclanchée a chaque fois qu'un onglet est lancé"""

        tabId = self.tabWidget.currentIndex()

        logMsg = "Id onglet: {0}".format(tabId)
        log.info(logMsg)

        # Planning
        if tabId == 0:
            log.info("Remplissage de l'onglet planning")
            self.planningtab__calendar__paint_cells()
            self.planningtab__watched__fill()
            self.planningtab__next__fill()
            self.pushButton_13.setEnabled(False)

        # Liste
        elif tabId == 1:
            self.listtab__serieslist__fill()

        # Notes
        elif tabId == 3:
            self.notestab__fill()

        # Paramètres
        elif tabId == 5:
            self.settings__fill()


    def profile__create(self):
        """Fonction qui crée un dossier de profil si il n'existe pas"""

        # Si le dossier est absent
        userFolder = Path.home()
        self.appDataFolder = os.path.join(userFolder, ".myanimemanager2")

        if not os.path.exists(self.appDataFolder):
            # Création du dossier ./profile/covers qui créer en meme temps le dossier parent ./profile
            os.makedirs(self.appDataFolder)
            log.info("Dossier de \"profile\" créer !")


    def database_(self):
        """"Fonction qui gère la créatio et l'ouverture de la base de données"""

        isDatabase = os.path.exists(os.path.join(self.appDataFolder, "database.sqlite3"))

        # Ouverture de la base de données
        self.database__open()

        # Si la base de données n'existe pas
        if not isDatabase:
            # Création des tables
            self.database__create_tables()

            # Remplissage des tables


    def database__open(self):
        """Ouvre la base de données et crée un curseur"""

        # Ouverture de la base
        self.database = sqlite3.connect(os.path.join(self.appDataFolder, "database.sqlite3"))

        # Accès facile aux colonnes (Par leur nom et nom par leur emplacement)
        self.database.row_factory = sqlite3.Row

        # Création d'un curseur SQL
        self.cursor = self.database.cursor()


    def database__create_tables(self):
        """"""

        # Exécution du code SQL
        self.cursor.execute(serieCreateTableQuery)
        self.cursor.execute(seasonCreateTableQuery)
        self.cursor.execute(planningCreateTableQuery)
        self.cursor.execute(notesCreateTableQuery)


    def listtab__seriemodal__open(self, titre, action, data):
        """Fonction d'ouverture de la fenètre modale série"""

        # Utilisé pour mémoriser la sélection de la combobox pour sélectionner la ligne après une modification
        self.currentSerieId = self.comboBox_2.currentIndex()

        # Création d'une instance de la classe
        self.seriemodal = SerieModal(self, action, data)

        # Définition du titre
        self.seriemodal.setWindowTitle(titre)

        # Rends la fenetre principale inacessible tant que celle-ci est ouverte
        self.seriemodal.setWindowModality(Qt.ApplicationModal)
        self.seriemodal.show()


    def listtab__seasonmodal__open(self, titre, action, serieData, seasonData):
        """Fonction d'ouverture de la fenètre modale saison"""

        # Utilisé pour mémoriser la sélection de la combobox pour sélectionner la ligne après une modification
        self.currentSeasonId = self.comboBox.currentIndex()

        # Création d'une instance de la classe
        self.seasonmodal = SeasonModal(self, action, serieData, seasonData)

        # Définition d'un titre
        self.seasonmodal.setWindowTitle(titre)

        # Rends la fenetre principale inacessible tant que celle-ci est ouverte
        self.seasonmodal.setWindowModality(Qt.ApplicationModal)
        self.seasonmodal.show()


    def listtab__series__changed(self):
        """Fonction appelée lorsque la sélection d'une série est changée"""

        # Remplisage des informations de la série
        log.info("self.listtab__series__changed --> self.listtab__seriedata__fill")
        self.listtab__seriedata__fill()

        # Remplissage de la liste des saisons
        log.info("self.listtab__series__changed --> self.listtab__seasonslist__fill")
        self.listtab__seasonslist__fill()


    def listtab__serieslist__set_current_index(self):
        """Fonction qui permet de remetre la sélection actuelle dans la combobox"""

        if len(self.seriesList) == 1:
            self.comboBox_2.setCurrentIndex(0)

        elif len(self.seriesList) > self.currentSerieId:
            index = self.currentSerieId
            self.comboBox_2.setCurrentIndex(index)


    def listtab__serieslist__search(self):
        """Fonction executée lors de l'entrée de texte dans la boite de recherche"""

        # Récupération de titre recherché
        searchPatern = self.lineEdit.text()

        # Remolissage de la liste avec les résultats
        self.listtab__serieslist__fill(searchPatern=searchPatern)


    def listtab__serieslist__search_clear(self):
        """Fonction qui vide la barre de recherche"""
        # Vide la liste
        self.lineEdit.setText("")

        # Rafraichi la liste des séries
        self.listtab__serieslist__fill()


    def listtab__serieslist__fill(self, searchPatern=None):
        """Fonction qui rempli la liste des séries"""

        # Nettoyage de la liste des saisons
        self.listtab__serieslist__clear()

        # Si aucune recherche n'est lancée, on affiche toute la liste des séries
        if searchPatern:
            sqlData = {'searchPatern': '%' + searchPatern + '%'} # Les % sont pour la condition LIKE: cela permet de rechercher un texte n'importe ou dans le titre
            self.cursor.execute(seriesGetListWhereQuery, sqlData)

        else:
            self.cursor.execute(seriesGetListQuery)

        self.seriesList = self.cursor.fetchall()

        # Remplissage du message de statistiques (nombre de séries)
        seriesCount = len(self.seriesList)
        self.statusbar.showMessage("Nombre de séries: {0}".format(seriesCount))

        if self.seriesList:
            # Remplissage de la liste des séries(Identifiant - Titre)
            for rowId, serie in enumerate(self.seriesList):
                serieSortId = serie["serieSortId"]
                serieTitle = serie["serieTitle"]

                serieItem = "{0} - {1}".format(serieSortId, serieTitle)
                self.comboBox_2.addItem(serieItem)

            self.listtab__serieslist__set_current_index()


    def listtab__serieslist__clear(self):
        """Fonction qui nettoye la liste des séries"""

        # Suppression des élements de la combobox
        self.comboBox_2.clear()


    def listtab__seriedata__fill(self):
        """Fonction qui rempli les champs d'informations de la série"""

        # Nettoyage des informations de la série
        self.listtab__seriedata__clear()

        # Récupération de l'identificant de l'élément sélectionné dans la liste des séries
        serieIndexId = self.comboBox_2.currentIndex()

        # Si une série est sélectionnée dans la liste
        if serieIndexId != -1:
            # Récupération de l'indentifiant de la série (comme les identfiants commence à 1
            serieData = self.seriesList[serieIndexId]
            serieId = str(serieData["serieId"])
            serieSortId = str(serieData["serieSortId"])
            serieTitle = str(serieData["serieTitle"])
            serieLiked = int(serieData["serieLiked"])
            self.seriePath = str(serieData["seriePath"])

            # Application des informations
            self.label_14.setText(serieSortId)
            self.label_13.setText(serieTitle)

            if os.path.exists(self.seriePath): self.pushButton_10.setEnabled(True)
            else: self.pushButton_10.setEnabled(False)

            # Affichage du logo si cette série est aimée
            if serieLiked == 1:
                # Application de l'image
                pixmap = QPixmap(os.path.join(self.appDir, icons["heart"]))
                self.label_34.setPixmap(pixmap)

            # Chargement de la cover depuis serieId
            pictureFilename = os.path.join(self.appDataFolder, "covers/{0}".format(serieId))
            if os.path.exists(pictureFilename):
                # Application de l'image
                pixmap = QPixmap(pictureFilename)
                self.label_30.setPixmap(pixmap)


    def listtab__seriedata__clear(self):
        """Fonction qui nettoye les informations d'une série"""

        self.label_14.setText("")  # Identifiant
        self.label_13.setText("")  # Titre
        self.seriePath = ""  # Chemin de la série

        # Nettoyage de l'icone coeur
        self.label_34.clear()

        # Application d'une image génerique en cas de cover introuvable
        pixmap = QPixmap(os.path.join(self.appDir, icons["cover"]))
        self.label_30.setPixmap(pixmap)


    def listtab__seasons__changed(self):
        """Fonction appelée lorsque la sélection d'une saison est changée"""

        # Nettoyage et remplisage de informations de la série
        log.info("self.listtab__seasons__changed --> self.listtab__seasondata__fill")
        self.listtab__seasondata__fill()


    def listtab__seasonslist__set_current_index(self):
        """Fonction qui permet de remetre la sélection actuelle dans la combobox"""

        if len(self.seasonsList) == 1:
            self.comboBox.setCurrentIndex(0)

        elif len(self.seasonsList) > self.currentSeasonId:
            index = self.currentSeasonId
            self.comboBox.setCurrentIndex(index)


    def listtab__seasonslist__fill(self):
        """Fonction qui remplie la liste des saisons pour la série choisie"""

        # Nettoyage de la liste des séries
        self.listtab__seasonslist__clear()

        # Si une série minimum existe
        if self.seriesList:

            # Récupération de l'identifiant de l'élément sélectionné dans la liste des séries
            serieIdList = self.comboBox_2.currentIndex()

            serieId = self.seriesList[serieIdList]["serieId"]

            log.info(seasonsGetListQuery)
            sqlData = {'serieId': serieId}
            self.cursor.execute(seasonsGetListQuery, sqlData)
            self.seasonsList = self.cursor.fetchall()

            # Si il existe des saisons pour cette série
            if self.seasonsList:
                serieSeasonsNumber = str(len(self.seasonsList))
                self.label_18.setText(serieSeasonsNumber)

            else:
                self.label_18.setText("Aucune")

            # Remplissage de la combobox
            for rowId, season in enumerate(self.seasonsList):
                seasonSortId = season["seasonSortId"]
                seasonTitle = season["seasonTitle"]
                seasonItem = "{0} - {1}".format(seasonSortId, seasonTitle)
                self.comboBox.addItem(seasonItem)

            self.listtab__seasonslist__set_current_index()


    def listtab__seasonslist__clear(self):
        """Liste qui nettoye la liste des saisons"""

        # Suppression des élements de la combobox
        self.comboBox.clear()


    def listtab__seasondata__fill(self):
        """Fonction qui remplie la liste des informations de la saison sélectionnée"""

        # Nettoyage des informations
        self.listtab__seasondata__clear()

        # Récupération de l'identifiant de l'élément sélectionné dans la liste des saisons
        seasonIndexId = self.comboBox.currentIndex()

        # Bug qui affiche les informations de la saison de la série précédente si la série choisie ne dispose pas de saison
        if seasonIndexId != -1:
            # Récupération des informations
            seasonData = self.seasonsList[seasonIndexId]
            seasonSortId = str(seasonData["seasonSortId"])
            seasonTitle = str(seasonData["seasonTitle"])
            seasonStudio = str(seasonData["seasonStudio"])
            seasonDescription = str(seasonData["seasonDescription"])
            seasonReleaseYear = str(seasonData["seasonReleaseYear"])
            seasonFansubTeam = str(seasonData["seasonFansubTeam"])
            seasonEpisodes = str(seasonData["seasonEpisodes"])
            seasonWatchedEpisodes = str(seasonData["seasonWatchedEpisodes"])
            seasonViewCount = str(seasonData["seasonViewCount"])
            seasonNotes = seasonData["seasonNotes"]
            seasonLanguageId = seasonData["seasonLanguage"]
            seasonLanguage = self.seasonLanguages[seasonLanguageId]
            seasonStateId = seasonData["seasonState"]
            seasonState = self.seasonStates[seasonStateId]

            # Application des informations
            self.label_24.setText(seasonSortId)
            self.label_5.setText(seasonTitle)
            self.label.setText(seasonStudio)
            self.label_23.setText(seasonDescription)
            self.label_7.setText(seasonReleaseYear)
            self.label_8.setText(seasonFansubTeam)
            self.label_20.setText(seasonEpisodes)
            self.label_21.setText(seasonWatchedEpisodes)
            self.label_28.setText(seasonViewCount)
            self.label_39.setText(seasonLanguage)
            self.label_32.setText(seasonState)
            self.label_35.setText(seasonNotes)


    def listtab__seasondata__clear(self):
        """Fonction qui nettoye la liste des informations de la saison sélectionnée"""

        self.label_24.clear()
        self.label_5.clear()
        self.label.clear()
        self.label_23.clear()
        self.label_7.clear()
        self.label_8.clear()
        self.label_20.clear()
        self.label_21.clear()
        self.label_39.clear()
        self.label_32.clear()
        self.label_28.clear()
        self.label_35.clear()


    def listtab__create_serie(self):
        """Fonction qui lance la fenetre de création d'une nouvelle série"""

        self.listtab__seriemodal__open("Ajouter", "create", None)


    def listtab__edit_serie(self):
        """Fonction qui lance la fenetre d'édition d'une série"""

        # Empèche d'éditer une série inexistante
        if not self.seriesList:
            # Si la liste est vide on affiche un message à l'utilisateur
            showInfo = QMessageBox.information(self, 'Action impossible', "Aucune saison à editer !", QMessageBox.Ok)

        else:
            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            serieIndexId = self.comboBox_2.currentIndex()

            # Récupération des informations
            serieData = self.seriesList[serieIndexId]
            serieTitle = serieData["serieTitle"]

            # Titre de la fenetre
            serieModalTitle = "Edition : %s" % serieTitle

            # Ouverture de la fenetre d'édition
            self.listtab__seriemodal__open(serieModalTitle, "edit", serieData)


    def listtab__delete_serie(self):
        """Fonction appelée pour la suppresion d'une série"""

        # Empèche de supprimer une série inexistante
        if not self.seriesList:
            # Si la liste est vide on affiche un message à l'utilisateur
            showInfo = QMessageBox.information(self, 'Action impossible', "Aucune saison à supprimer !", QMessageBox.Ok)

        else:
            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            serieIndexId = self.comboBox_2.currentIndex()

            # Récupération des informations
            serieData = self.seriesList[serieIndexId]
            serieId = serieData["serieId"]
            sqlData = {'serieId': serieId}

            # Suppression de la série dans dans le planning (évite de garder des séries dans le planning)
            log.info(serieDeleteFromPlanningQuery)
            self.cursor.execute(serieDeleteFromPlanningQuery, sqlData)

            # Suppression des saisons
            log.info(seasonDeleteFromSeasonsWhereSerieIdQuery)
            self.cursor.execute(seasonDeleteFromSeasonsWhereSerieIdQuery, sqlData)

            # Suppression de la série
            log.info(serieDeleteFromSeriesQuery)
            self.cursor.execute(serieDeleteFromSeriesQuery, sqlData)

            # Mise à jour de la liste des séries et des informations
            self.listtab__serieslist__fill()
            self.listtab__seriedata__fill()
            self.listtab__seasonslist__fill()
            self.listtab__seasondata__fill()


    def listtab__create_season(self):
        """Fonction qui lance la fenetre de création d'une nouvelle saison"""

        # Empèche de créer une saison si aucune série n'existe
        if not self.seriesList:
            # Si la liste est vide on affiche un message à l'utilisateur
            showInfo = QMessageBox.information(self, 'Action impossible', "Aucune série existante !", QMessageBox.Ok)

        else:

            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            serieIndexId = self.comboBox_2.currentIndex()

            # Récupération des informations
            serieData = self.seriesList[serieIndexId]
            serieId = serieData["serieId"]

            # Ouverture de la fenetre modale
            self.listtab__seasonmodal__open("Ajouter", "create", serieId, None)


    def listtab__edit_season(self):
        """Fonction qui lance la fenetre d'edition d'une saison"""

        # Empèche d'éditer une saison inexistante
        if not self.seasonsList:
            # Si la liste est vide on affiche un message à l'utilisateur
            showInfo = QMessageBox.information(self, 'Action impossible', "Aucune saison à editer !", QMessageBox.Ok)

        else:
            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            serieIndexId = self.comboBox_2.currentIndex()

            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            seasonIndexId = self.comboBox.currentIndex()

            # Récupération d'information sur la série
            serieData = self.seriesList[serieIndexId]
            serieId = serieData["serieId"]

            # Récupération des informations sur la saison
            seasonData = self.seasonsList[seasonIndexId]
            seasonTitle = seasonData["seasonTitle"]

            # Titre de la fenetre
            seasonModalTitle = "Edition : %s" % seasonTitle

            # Ouverture de la fenetre d'édition
            self.listtab__seasonmodal__open(seasonModalTitle, "edit", serieId, seasonData)


    def listtab__delete__season(self):
        """Fonction qui supprime la saison sélectionnée"""

        # Empèche de supprimer une saison inexistante
        if not self.seasonsList:
            # Si la liste est vide on affiche un message à l'utilisateur
            showInfo = QMessageBox.information(self, 'Action impossible', "Aucune saison à supprimer !", QMessageBox.Ok)

        else:

            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            seasonIndexId = self.comboBox.currentIndex()

            # Récupération des informations sur la saison
            seasonData = self.seasonsList[seasonIndexId]
            seasonId = seasonData["seasonId"]
            sqlData = {'seasonId': seasonId}

            # Suppression de la saison dans dans le planning (évite de garder des saisons dans le planning)
            log.info(seasonDeleteFromPlanningQuery)
            self.cursor.execute(seasonDeleteFromPlanningQuery, sqlData)

            # Suppression des saisons
            log.info(seasonDeleteFromSeasonsQuery)
            self.cursor.execute(seasonDeleteFromSeasonsQuery, sqlData)

            # Mise à jour de l'interface
            self.listtab__serieslist__fill()
            self.listtab__seriedata__fill()

    def listtab__random_serie(self):
        self.listtab__serieslist__fill()

        if self.seriesList:
            serieId = randint(0, len(self.self.seriesList))
            self.comboBox_2.setCurrentIndex(serieId)


    def listtab__open_explorer(self):
        """Fonction qui ouvre un gestionnaire de fichiers. Multiplatforme"""

        # Récupération du chemin du dossier de la série en cours
        path = self.seriePath

        if path:
            if not open_filebrowser(path): log.info("Impossible d'ouvrir le répertoire")


    def planningtab__calendar__paint_cells(self):
        """
        Met à jour les jours où des épisodes ont étés vus (colore le fond du jour)

        :return:
        """

        self.planningCalendar.cellsCondition.clear()
        log.info(planningDateFromPlanningQuery)
        self.cursor.execute(planningDateFromPlanningQuery)
        rows = self.cursor.fetchall()

        for row in rows:
            date = QDate.fromString(row[0], "yyyy-MM-dd")
            self.planningCalendar.cellsCondition.append(QDate(date))

        self.planningCalendar.paintCell(QPainter(), QRect(), QDate())



    def planningtab__watched__clear(self):
        """Fonction qui vide la liste des séries vues"""

        # Vidage du tableau
        # Efface le contenu
        self.tableWidget_2.clearContents()

        # Supprime les lignes vides
        self.tableWidget_2.setRowCount(0)


    def planningtab__watched__fill(self):
        """Fonction qui rempli la listes des séries vus en fonction de la date"""

        # Nettoyage de la liste
        self.planningtab__watched__clear()

        # Nettoyage du nombre d'épisodes vus pour cette date
        self.label_37.setText("")

        # Récupération de la date en cours dans le calendrier
        selectedDate = self.planningCalendar.selectedDate().toPyDate()

        log.info(getDataForTheChoosenDay)
        sqlData = {'planningDate': selectedDate}
        self.cursor.execute(getDataForTheChoosenDay, sqlData)
        self.planningWatched = self.cursor.fetchall()

        # Affichage du nombre d'épisodes vus pour cette date
        episodesCount = len(self.planningWatched)
        if episodesCount < 2:
            text = "épisode vu"
        else:
            text = "épisodes vus"

        message = "{0} {1}".format(episodesCount, text)

        # Application du message
        self.label_37.setText(message)

        # Remplissage de la liste des séries vues (si elle n'est pas vide)
        if self.planningWatched:

            # Définition de la taille du tableau
            rowNumber = len(self.planningWatched)
            self.tableWidget_2.setRowCount(rowNumber)

            # Ajout des éléments
            for id, row in enumerate(self.planningWatched):
                # On affiche pas la colonne de la date
                # Récupération des informations

                serieTitle = row["serieTitle"]
                seasonTitle = row["seasonTitle"]
                planningEpisodeId = str(row["planningEpisodeId"])

                # Ajout des colonnes dans le tableau
                column0 = QTableWidgetItem(serieTitle)
                self.tableWidget_2.setItem(id, 0, column0)

                column1 = QTableWidgetItem(seasonTitle)
                self.tableWidget_2.setItem(id, 1, column1)

                column2 = QTableWidgetItem(planningEpisodeId)
                self.tableWidget_2.setItem(id, 2, column2)

        # Taille de cellules s'adaptant au contenu
        self.tableWidget_2.resizeColumnsToContents()


    def planningtab__watched__add(self):
        """Fonction qui ajoute l'épisode à voir dans la liste des épisodes vus"""

        # Récupération de l'identifiant sélectionné
        planningtabNextIndex = self.tableWidget_3.currentRow()

        if planningtabNextIndex != -1:

            # Récupération de la date sélectionnée
            selectedDate = self.planningCalendar.selectedDate().toPyDate()

            # Récupération des informations sur l'élement sélectionné
            data = self.planningToWatch[planningtabNextIndex]
            serieId = data["serieId"]
            seasonId = data["seasonId"]
            seasonEpisodes = data["seasonEpisodes"]
            seasonWatchedEpisodes = data["seasonWatchedEpisodes"]
            seasonCurrentEpisodeId = seasonWatchedEpisodes + 1

            # Commande SQL d'insertion dans les animés vus
            log.info(planningAddEpisodeToWatchedList)
            sqlData = {'selectedDate': selectedDate, 'serieId': serieId, 'seasonId': seasonId, 'seasonCurrentEpisodeId': seasonCurrentEpisodeId}
            self.cursor.execute(planningAddEpisodeToWatchedList, sqlData)

            # Incrémentation du nombre d'épisodes vus pour la saison
            # Si la saison est terminée, alors
            if seasonCurrentEpisodeId == seasonEpisodes:

                # On passe le nombre d'épisodes vus à 0
                log.info(planningSetCurrentEpisodeTo0)
                sqlData = {'seasonId': seasonId}
                self.cursor.execute(planningSetCurrentEpisodeTo0, sqlData)

                # On incrémente le nombre de visionnages
                log.info(planningIncrementSeasonViewCount)
                self.cursor.execute(planningIncrementSeasonViewCount, sqlData)

                # On passe l'état de la série à 3: terminé
                log.info(planningSetSeasonToFinished)
                self.cursor.execute(planningSetSeasonToFinished, sqlData)

            # Sinon on incrémente normalement
            else:
                sqlData = {'seasonWatchedEpisodes': seasonCurrentEpisodeId, 'seasonId': seasonId}
                self.cursor.execute(planningIncrementEpisode, sqlData)

            # Mise à jour des couleurs de fond des jours dans le calendrier
            self.planningtab__calendar__paint_cells()

            # Mise à jour de la liste des épisodes vus
            self.planningtab__watched__fill()

            # Mise à jour de la liste des épisodes à voir
            self.planningtab__next__fill()


    def planningtab__watched__remove(self):
        """Fonction qui supprime une série dans la liste"""

        # Récupération de l'identifiant de la ligne sélectionnée
        currentId = self.tableWidget_2.currentRow()

        if currentId != -1:
            data = self.planningWatched[currentId]
            planningId = data["planningId"]

            log.info(planningRemoveEpisodeFromWatchedList)
            sqlData = {'planningId': planningId}
            self.cursor.execute(planningRemoveEpisodeFromWatchedList, sqlData)

            # Mise à jour des couleurs de fond des jours dans le calendrier
            self.planningtab__calendar__paint_cells()

            # Mise à jour de la liste des épisodes vus
            self.planningtab__watched__fill()


    def planningtab__is_button_need_to_be_enabled(self):
        """Affiche ou masque le bouton d'ouverture si le dossier de la série n'existe pas"""

        planningtabNextIndex = self.tableWidget_3.currentRow()
        if planningtabNextIndex != -1:
            # Récupération des informations sur l'élement sélectionné
            data = self.planningToWatch[planningtabNextIndex]
            seriePath = data["seriePath"]

            if os.path.exists(seriePath): self.pushButton_13.setEnabled(True)
            else: self.pushButton_13.setEnabled(False)


    def planningtab__next__clear(self):
        """Fonction qui vide la liste des épisodes à voir"""

        # Vidage du tableau
        # Efface le contenu
        self.tableWidget_3.clearContents()

        # Supprime les lignes vides
        self.tableWidget_3.setRowCount(0)


    def planningtab__next__fill(self):
        """Fonction qui remplie la liste des épisodes à voir"""

        # Nettoyage des informations dans le tableau
        self.planningtab__next__clear()

        # Si on choisi de n'afficher que les séries en cours
        if self.checkBox.isChecked():
            # Commande SQL
            sqlQuery = planningFillWithWatchingSeries

        else:
            # Commande SQL
            sqlQuery = planningEpisodesFillWithAll

        log.info(sqlQuery)
        self.cursor.execute(sqlQuery)
        self.planningToWatch = self.cursor.fetchall()

        # Remplissage de la liste des séries vues (si elle n'est pas vide)
        if self.planningToWatch:

            # Définition de la taille du tableau
            rowNumber = len(self.planningToWatch)
            self.tableWidget_3.setRowCount(rowNumber)

            # Ajout des éléments
            for id, row in enumerate(self.planningToWatch):
                # Récupération des informations
                serieTitle = row["serieTitle"]
                seasonTitle = row["seasonTitle"]
                planningEpisodeId = row["seasonWatchedEpisodes"]  # Identifiant du prochain épisode
                planningEpisodeIdNext = row["seasonWatchedEpisodes"] + 1
                planningEpisodes = row["seasonEpisodes"]
                plannningEpisodeIdTotal = "{} sur {}".format(planningEpisodeIdNext, planningEpisodes)

                # Ajout des colonnes dans le tableau
                column0 = QTableWidgetItem(serieTitle)
                self.tableWidget_3.setItem(id, 0, column0)

                column1 = QTableWidgetItem(seasonTitle)
                self.tableWidget_3.setItem(id, 1, column1)

                column2 = QTableWidgetItem(plannningEpisodeIdTotal)
                self.tableWidget_3.setItem(id, 2, column2)

                progressBar = QProgressBar(self)
                progressBar.setMinimum(0)
                progressBar.setMaximum(planningEpisodes)
                progressBar.setValue(planningEpisodeId) # Car si un film donc épisode 1 / 1 on à déja une barre à 100%

                self.tableWidget_3.setCellWidget(id, 3, progressBar)


        # Taille de cellules s'adaptant au contenu
        self.tableWidget_3.resizeColumnsToContents()


    def planningtab__calendar__today(self):
        """Fonction qui ramène le calendrier à la date actuelle"""

        # Récupère la date du jour
        today = QDate.currentDate()

        # Affiche le calendrier à la date du jour
        self.planningCalendar.setSelectedDate(today)

        # Met à jour les informations
        self.planningtab__watched__fill()


    def planningtab__open_explorer(self):
        """Fonction qui ouvre un gestionnaire de fichiers. Multiplatforme"""

        # Récupération de l'identifiant sélectionné dans le tableau des animés à voir
        planningtabNextIndex = self.tableWidget_3.currentRow()

        if planningtabNextIndex != -1:

            # Récupération des informations sur l'élement sélectionné
            data = self.planningToWatch[planningtabNextIndex]
            seriePath = data["seriePath"]

            if seriePath:
                if not open_filebrowser(seriePath): log.info("Impossible d'ouvrir le répertoire")


    def notestab__fill(self):
        """Fonction qui rempli les notes"""

        log.info(notesGet)
        self.cursor.execute(notesGet)

        notes = self.cursor.fetchone()

        # Si il y a une notes existantes:
        if notes:
            notesPageId = notes["notesPageId"]
            notesData = notes["notesData"]

            self.plainTextEdit.setPlainText(notesData)


    def notestab__save(self):
        """Fonction qui sauvegarde les notes"""

        # Récupération des données
        notesData = self.plainTextEdit.toPlainText()

        # Enregistrement des notes dans la base de données
        sqlData = {'notesData': notesData}
        self.cursor.execute(notesSave, sqlData)


    def settings__load(self):
        """Fonction qui charge les paramètres depuis le fichier de configuration"""

        # Si le fichier de paramètres existe
        if os.path.exists(os.path.join(self.appDataFolder, "settings.json")):

            log.info("Fichier de paramètres trouvé. Chargement des informations ...")

            # Ouverture du fichier json
            with open(os.path.join(self.appDataFolder, "settings.json"), "r") as settingsFile:

                # Chargement avec la bibliotheque JSON
                self.settings = load(settingsFile)

        else:
            log.info("Aucun fichier de paramètres trouvé. Utilisation des parametres par défaut")

            # Utilisation des paramètres par défaut
            self.settings = self.defaultSettings

            # Création d'un fichier de configuration
            self.settings__save()


    def settings__fill(self):
        """Fonction qui rempli les parametres dans l'onglet associé"""

        log.info("Chargement des paramètres dans les élements de l'onglet Paramètres")


        # Application des informations sur les controles visuels
        self.comboBox_3.setCurrentIndex(self.settings["startupPageId"])
        self.checkBox_2.setChecked(self.settings["realtimeSearch"])


    def settings__save(self):
        """Fonction utilisé pour sauvegarder la configuration"""

        # Application des nouveaux parametres
        self.settings["startupPageId"] = self.comboBox_3.currentIndex()
        self.settings["realtimeSearch"] = self.checkBox_2.isChecked()

        # Ouverture ou création du fichier de configuration
        with open(os.path.join(self.appDataFolder, 'settings.json'), 'w') as settingsFile:
            log.info("Sauvegarde des paramètres")

            # Sauvegarde des paramètres avec JSON
            dump(self.settings, settingsFile)

        self.statusbar.showMessage("Paramètres sauvegardés. Relancer l'application pour qu'ils prennent effet.")


    # Fonctions de l'onglet outils
    def tools__watch_time__execute(self):
        """Fonction qui permet d'établir un planning """

        # Effacement de la liste
        self.listWidget_2.clear()

        # Récupération du contenu des spinbox
        episodeNumber = self.spinBox_2.value()
        episodeLength = self.spinBox_3.value()

        # Récupération de l'heure de départ à partir de la textbox  et la convertion en string
        startString = str(self.timeEdit.dateTime().toString("hh:mm"))  # time().toPyTime()

        # Convertion de la chaine en type datetime
        start = datetime.strptime(startString, "%H:%M")

        for x in range(episodeNumber):
            end = start + timedelta(minutes=episodeLength)
            rowText = "{:02d} - {:02d}:{:02d} -> {:02d}:{:02d}".format(x + 1, start.hour, start.minute, end.hour,
                                                                       end.minute)  # Chaine qui sera affichée

            # Création de l'élément
            row = QListWidgetItem(rowText)

            # Ajout de l'élément dans le tableau
            self.listWidget_2.addItem(row)

            # Décale la plage
            start = end


    def tools__watch_time__local_time(self):
        """Fonction qui permet de choisir l'heure actuelle dans l'outil"""

        # Récupération de l'heure locale
        localTime = QTime.currentTime()

        # Application de l'heure sur l'objet timeEdit
        self.timeEdit.setTime(localTime)


    def on_close(self, event):
        """Action appelée à la fermeture de l'application"""

        # Si il y a eu des modifications
        if self.database.total_changes > 0:

            # Affiche la fenetre de dialogue d'enregistrement
            saveQuestion = QMessageBox.question(self, 'Enregistrer les changements', "Enregistrer les modifications ?", QMessageBox.Yes, QMessageBox.No)

            # Si on clique sur Oui (Sauvegarder)
            if saveQuestion == QMessageBox.Yes:
                # Enregistre les modifications dans la bdd
                self.database.commit()

            # Si on clique sur Quitter sans sauvegarder
            elif saveQuestion == QMessageBox.No:

                # Annule tout les changements depuis le dernier enregistrement
                self.database.rollback()
