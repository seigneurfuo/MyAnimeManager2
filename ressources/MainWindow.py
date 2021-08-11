import csv

from PyQt5.QtCore import QTime, Qt, QDate, QRect, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.QtGui import QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QMessageBox, QListWidgetItem, QMainWindow, QTableWidgetItem, QProgressBar
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
import platform

# Modules locaux
from ressources.ressource import icons  # Chemins vers les fichiers (TODO: à remplacer dans le futur par un qrc)
from ressources.utils import *
from ressources.calendar import Calendar


class MainWindow(QMainWindow):
    """Classe de la fenetre princinpale"""

    def __init__(self, version, app_dir):
        """

        :param version: La version de l'application (uniquement pour afficher le titre et
        :param app_dir:
        """

        super(MainWindow, self).__init__()

        # Répertoire de travail de l'application lancée
        self.appDir = app_dir
        self.app_version = version

        self.defaultSettings = {"startupPageId": 1, "realtimeSearch": False}
        self.settings = {}

        self.seriesList = []
        self.serie_path = ""
        self.currentSerieId = 0

        self.seasonsList = []
        self.currentSeasonId = 0
        self.seasonStates = ["Indéfinie", "A voir", "En cours", "Terminée", "Annulée"]
        self.seasonLanguages = ["Indéfinie", "Japonais", "Japonais & Francais (Dual Audio)", "Français", "Autres"]

        self.planning_watched = []
        self.planningToWatch = []

        # Indique si les modifications on eté sauvegardées (permet d'afficher un message uniquement si il y a des
        # informations à sauvegarder)
        self.unsaved = False

        # Création du profil
        self.profile__create()

        # Vérification / Création de la base de données
        self.database_()

        # Initialise l'affichage
        self.setup_ui()

        # Chargement des paramètres
        self.settings__load()

        # Chargement des évenements des élements de l'interface
        self.events()

        # Chargement des evenement par rapport à l'onglet
        self.on_tab_changed()

        # Définition du premier onglet affiché (ici car c'est un parametre qui n'est utilisé qu'au démarrage
        self.tabWidget.setCurrentIndex(self.settings["startupPageId"])

    def setup_ui(self):
        loadUi(os.path.join(self.appDir, 'ressources/MainWindow.ui'), self)

        # Chargement du calendrier personalisé
        self.planningCalendar = Calendar()
        self.planningCalendar.setCellsBackgroundColor(QColor(115, 210, 22, 50))
        self.horizontalLayout_31.insertWidget(0, self.planningCalendar, )

        window_title = "MyAnimeManager2 - version {0}".format(self.app_version)
        self.setWindowTitle(window_title)

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
        self.season_dates_checkbox.clicked.connect(self.planningtab__on_season_dates_state_changed)

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
            self.lineEdit.textChanged.connect(
                self.listtab__serieslist__search)  # Barre de recherche de série (recherche en direct)

        self.pushButton_14.clicked.connect(self.listtab__serieslist__search_clear)  # Bouton de nettoyage de la liste

        # Evenement des listes de sélections (séries et saisons)
        self.comboBox_2.currentIndexChanged.connect(self.listtab__series__changed)
        self.comboBox.currentIndexChanged.connect(self.listtab__seasons__changed)

        # ----- Onglet outils -----
        self.pushButton_7.clicked.connect(self.tools__watch_time__execute)
        self.pushButton_8.clicked.connect(self.tools__watch_time__local_time)

        # ----- Onglet notes -----
        self.pushButton_12.clicked.connect(self.notestab__save)

        # ----- Stats -----
        self.pushButton_15.clicked.connect(self.export_seasons_list)

        # ----- Onglet paramètres -----
        self.pushButton_11.clicked.connect(self.settings__save)

    def on_tab_changed(self):
        """Fonction déclanchée a chaque fois qu'un onglet est lancé"""

        tab_id = self.tabWidget.currentIndex()

        print("Tab ID:", tab_id)

        # Planning
        if tab_id == 0:
            self.planningtab__calendar__paint_cells()
            self.planningtab__watched__fill()
            self.planningtab__next__fill()
            self.pushButton_13.setEnabled(False)

        # Liste
        elif tab_id == 1:
            self.listtab__serieslist__fill()

        # Liste 2
        elif tab_id == 2:
            self.fulllisttab_table_fill()

        # Notes
        elif tab_id == 4:
            self.notestab__fill()

        # Tab Id
        elif tab_id == 5:
            self.stats__fill()

        # Paramètres
        elif tab_id == 6:
            self.settings__fill()

        # A propos
        elif tab_id == 7:
            self.fill_about_data()

    def profile__create(self):
        """Fonction qui crée un dossier de profil si il n'existe pas"""

        # Recherche du profil à coté du programme, sinon recherche dans le dossier utilisateur
        local_profile_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".myanimemanager2")

        if os.path.exists(local_profile_path):
            self.appDataFolder = local_profile_path

        else:
            user_folder = Path.home()
            self.appDataFolder = os.path.join(user_folder, ".myanimemanager2")

            if not os.path.exists(self.appDataFolder):
                # Création du dossier ./profile/covers qui créer en meme temps le dossier parent ./profile
                os.makedirs(self.appDataFolder)
                print("Dossier de \"profil\" créer !")

        print("Dossier du profil: {}".format(self.appDataFolder))

    def database_(self):
        """"Fonction qui gère la créatio et l'ouverture de la base de données"""

        is_database = os.path.exists(os.path.join(self.appDataFolder, "database.sqlite3"))

        # Ouverture de la base de données
        self.database__open()

        # Si la base de données n'existe pas
        if not is_database:
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

    def listtab__seasonmodal__open(self, titre, action, serie_data, season_data):
        """Fonction d'ouverture de la fenètre modale saison"""

        # Utilisé pour mémoriser la sélection de la combobox pour sélectionner la ligne après une modification
        self.currentSeasonId = self.comboBox.currentIndex()

        # Création d'une instance de la classe
        self.seasonmodal = SeasonModal(self, action, serie_data, season_data)

        # Définition d'un titre
        self.seasonmodal.setWindowTitle(titre)

        # Rends la fenetre principale inacessible tant que celle-ci est ouverte
        self.seasonmodal.setWindowModality(Qt.ApplicationModal)
        self.seasonmodal.show()

    def listtab__series__changed(self):
        """Fonction appelée lorsque la sélection d'une série est changée"""

        # Remplisage des informations de la série
        self.listtab__seriedata__fill()

        # Remplissage de la liste des saisons
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
        search_patern = self.lineEdit.text()

        # Remolissage de la liste avec les résultats
        self.listtab__serieslist__fill(search_patern=search_patern)

    def listtab__serieslist__search_clear(self):
        """Fonction qui vide la barre de recherche"""
        # Vide la liste
        self.lineEdit.setText("")

        # Rafraichi la liste des séries
        self.listtab__serieslist__fill()

    def listtab__serieslist__fill(self, search_patern=None):
        """Fonction qui rempli la liste des séries"""

        # Nettoyage de la liste des saisons
        self.listtab__serieslist__clear()

        # Si aucune recherche n'est lancée, on affiche toute la liste des séries
        if search_patern:
            sql_data = {
                'searchPatern': '%' + search_patern + '%'}  # Les % sont pour la condition LIKE: cela permet de
            # rechercher un texte n'importe ou dans le titre
            self.cursor.execute(seriesGetListWhereQuery, sql_data)

        else:
            self.cursor.execute(seriesGetListQuery)

        self.seriesList = self.cursor.fetchall()

        # Remplissage du message de statistiques (nombre de séries)

        series_count = len(self.seriesList)
        if series_count > 0:
            self.cursor.execute(lastEpisodeWatchedDate)
            last_episode_date = self.cursor.fetchone()[0]
            self.statusbar.showMessage(
                "Nombre de séries: {0} - Dernier épisode vu le: {1}".format(series_count, last_episode_date))

        if self.seriesList:
            # Remplissage de la liste des séries(Identifiant - Titre)
            for rowId, serie in enumerate(self.seriesList):
                serie_sort_id = serie["serie_sort_id"]
                serie_title = serie["serie_title"]

                serie_item = "{0} - {1}".format(serie_sort_id, serie_title)
                self.comboBox_2.addItem(serie_item)

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
        serie_index_id = self.comboBox_2.currentIndex()

        # Si une série est sélectionnée dans la liste
        if serie_index_id != -1:
            # Récupération de l'indentifiant de la série (comme les identfiants commence à 1
            serie_data = self.seriesList[serie_index_id]
            serie_id = str(serie_data["serie_id"])
            serie_sort_id = str(serie_data["serie_sort_id"])
            serie_title = str(serie_data["serie_title"])
            serie_liked = int(serie_data["serie_liked"])
            self.serie_path = str(serie_data["serie_path"])

            # Application des informations
            self.label_14.setText(serie_sort_id)
            self.label_13.setText(serie_title)

            if os.path.exists(self.serie_path):
                self.pushButton_10.setEnabled(True)
            else:
                self.pushButton_10.setEnabled(False)

            # Affichage du logo si cette série est aimée
            if serie_liked == 1:
                # Application de l'image
                pixmap = QPixmap(os.path.join(self.appDir, icons["heart"]))
                self.label_34.setPixmap(pixmap)

            # Chargement de la cover depuis serie_id
            picture_filename = os.path.join(self.appDataFolder, "covers/{0}".format(serie_id))
            if os.path.exists(picture_filename):
                # Application de l'image
                pixmap = QPixmap(picture_filename)
                self.label_30.setPixmap(pixmap)

    def listtab__seriedata__clear(self):
        """Fonction qui nettoye les informations d'une série"""

        self.label_14.clear()  # Identifiant
        self.label_13.clear()  # Titre
        self.serie_path = ""  # Chemin de la série

        # Nettoyage de l'icone coeur
        self.label_34.clear()

        # Application d'une image génerique en cas de cover introuvable
        pixmap = QPixmap(os.path.join(self.appDir, icons["cover"]))

        self.label_30.setScaledContents(True)
        self.label_30.setPixmap(pixmap)

    def listtab__seasons__changed(self):
        """Fonction appelée lorsque la sélection d'une saison est changée"""

        # Nettoyage et remplisage de informations de la série
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
            serie_id_list = self.comboBox_2.currentIndex()

            serie_id = self.seriesList[serie_id_list]["serie_id"]

            sql_data = {'serie_id': serie_id}
            self.cursor.execute(seasonsGetListQuery, sql_data)
            self.seasonsList = self.cursor.fetchall()

            # Si il existe des saisons pour cette série
            if self.seasonsList:
                serie_seasons_number = str(len(self.seasonsList))
                self.label_18.setText(serie_seasons_number)

            else:
                self.label_18.setText("Aucune")

            # Remplissage de la combobox
            for rowId, season in enumerate(self.seasonsList):
                season_sort_id = season["season_sort_id"]
                season_title = season["season_title"]
                season_item = "{0} - {1}".format(season_sort_id, season_title)
                self.comboBox.addItem(season_item)

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
        season_index_id = self.comboBox.currentIndex()

        # Bug qui affiche les informations de la saison de la série précédente si la série choisie ne dispose pas de
        # saison
        if season_index_id != -1:
            # Récupération des informations
            season_data = self.seasonsList[season_index_id]
            season_sort_id = str(season_data["season_sort_id"])
            season_title = str(season_data["season_title"])
            season_studio = str(season_data["season_studio"])
            season_description = str(season_data["season_description"])
            season_release_year = str(season_data["season_release_year"])
            season_fansub_team = str(season_data["season_fansub_team"])
            season_episodes = str(season_data["season_episodes"])
            season_watched_episodes = str(season_data["season_watched_episodes"])
            season_view_count = str(season_data["season_view_count"])
            season_notes = season_data["season_notes"]
            season_language_id = season_data["season_language"]
            season_language = self.seasonLanguages[season_language_id]
            season_state_id = season_data["season_state"]
            season_state = self.seasonStates[season_state_id]

            # Sites web
            anidb = href_link(season_data["anidb"])
            animeka = href_link(season_data["animeka"])
            animekun = href_link(season_data["animekun"])
            animenewsnetwork = href_link(season_data["animenewsnetwork"])
            myanimelist = href_link(season_data["myanimelist"])
            planetejeunesse = href_link(season_data["planetejeunesse"])

            # Application des informations
            self.label_24.setText(season_sort_id)
            self.label_5.setText(season_title)
            self.label.setText(season_studio)
            self.label_23.setText(season_description)
            self.label_7.setText(season_release_year)
            self.label_8.setText(season_fansub_team)
            self.label_20.setText(season_episodes)
            self.label_21.setText(season_watched_episodes)
            self.label_28.setText(season_view_count)
            self.label_39.setText(season_language)
            self.label_32.setText(season_state)
            self.label_35.setText(season_notes)
            self.label_52.setText(anidb)
            self.label_54.setText(animeka)
            self.label_56.setText(animekun)
            self.label_58.setText(animenewsnetwork)

            # TODO myanimelist & planetejeunesse

    def listtab__seasondata__clear(self):
        """Fonction qui nettoye la liste des informations de la saison sélectionnée"""

        labels = [self.label_24, self.label_5, self.label, self.label_23, self.label_7, self.label_8, self.label_20,
                  self.label_21, self.label_39, self.label_32, self.label_28, self.label_35, self.label_52,
                  self.label_56, self.label_54, self.label_58]

        for label_name in labels:
            label_name.clear()

    def listtab__create_serie(self):
        """Fonction qui lance la fenetre de création d'une nouvelle série"""

        self.listtab__seriemodal__open("Ajouter", "create", None)

    def listtab__edit_serie(self):
        """Fonction qui lance la fenetre d'édition d'une série"""

        # Empèche d'éditer une série inexistante
        if not self.seriesList:
            # Si la liste est vide on affiche un message à l'utilisateur
            show_info = QMessageBox.information(self, 'Action impossible', "Aucune saison à editer !", QMessageBox.Ok)

        else:
            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            serie_index_id = self.comboBox_2.currentIndex()

            # Récupération des informations
            serie_data = self.seriesList[serie_index_id]
            serie_title = serie_data["serie_title"]

            # Titre de la fenetre
            serie_modal_title = "Edition : %s" % serie_title

            # Ouverture de la fenetre d'édition
            self.listtab__seriemodal__open(serie_modal_title, "edit", serie_data)

    def listtab__delete_serie(self):
        """Fonction appelée pour la suppresion d'une série"""

        # Empèche de supprimer une série inexistante
        if not self.seriesList:
            # Si la liste est vide on affiche un message à l'utilisateur
            show_info = QMessageBox.information(self, 'Action impossible', "Aucune saison à supprimer !",
                                                QMessageBox.Ok)

        else:
            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            serie_index_id = self.comboBox_2.currentIndex()

            # Récupération des informations
            serie_data = self.seriesList[serie_index_id]
            serie_id = serie_data["serie_id"]
            sql_data = {'serie_id': serie_id}

            # Suppression de la série dans dans le planning (évite de garder des séries dans le planning)
            self.cursor.execute(serieDeleteFromPlanningQuery, sql_data)

            # Suppression des saisons
            self.cursor.execute(seasonDeleteFromSeasonsWhereSerie_idQuery, sql_data)

            # Suppression de la série
            self.cursor.execute(serieDeleteFromSeriesQuery, sql_data)

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
            show_info = QMessageBox.information(self, 'Action impossible', "Aucune série existante !", QMessageBox.Ok)

        else:

            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            serie_index_id = self.comboBox_2.currentIndex()

            # Récupération des informations
            serie_data = self.seriesList[serie_index_id]
            serie_id = serie_data["serie_id"]

            # Ouverture de la fenetre modale
            self.listtab__seasonmodal__open("Ajouter", "create", serie_id, None)

    def listtab__edit_season(self):
        """Fonction qui lance la fenetre d'edition d'une saison"""

        # Empèche d'éditer une saison inexistante
        if not self.seasonsList:
            # Si la liste est vide on affiche un message à l'utilisateur
            show_info = QMessageBox.information(self, 'Action impossible', "Aucune saison à editer !", QMessageBox.Ok)

        else:
            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            serie_index_id = self.comboBox_2.currentIndex()

            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            season_index_id = self.comboBox.currentIndex()

            # Récupération d'information sur la série
            serie_data = self.seriesList[serie_index_id]
            serie_id = serie_data["serie_id"]

            # Récupération des informations sur la saison
            season_data = self.seasonsList[season_index_id]
            season_title = season_data["season_title"]

            # Titre de la fenetre
            season_modal_title = "Edition : %s" % season_title

            # Ouverture de la fenetre d'édition
            self.listtab__seasonmodal__open(season_modal_title, "edit", serie_id, season_data)

    def listtab__delete__season(self):
        """Fonction qui supprime la saison sélectionnée"""

        # Empèche de supprimer une saison inexistante
        if not self.seasonsList:
            # Si la liste est vide on affiche un message à l'utilisateur
            show_info = QMessageBox.information(self, 'Action impossible', "Aucune saison à supprimer !",
                                                QMessageBox.Ok)

        else:

            # Récupération de l'index de la série sélectionnée dans la liste déroulante
            season_index_id = self.comboBox.currentIndex()

            # Récupération des informations sur la saison
            season_data = self.seasonsList[season_index_id]
            season_id = season_data["season_id"]
            sql_data = {'season_id': season_id}

            # Suppression de la saison dans dans le planning (évite de garder des saisons dans le planning)
            self.cursor.execute(seasonDeleteFromPlanningQuery, sql_data)

            # Suppression des saisons
            self.cursor.execute(seasonDeleteFromSeasonsQuery, sql_data)

            # Mise à jour de l'interface
            self.listtab__serieslist__fill()
            self.listtab__seriedata__fill()

    def listtab__random_serie(self):
        self.listtab__serieslist__fill()

        if self.seriesList:
            serie_id = randint(0, len(self.seriesList))
            self.comboBox_2.setCurrentIndex(serie_id)

    def listtab__open_explorer(self):
        """Fonction qui ouvre un gestionnaire de fichiers. Multiplatforme"""

        # Récupération du chemin du dossier de la série en cours
        path = self.serie_path

        if path:
            if not open_file_explorer(path):
                print("Impossible d'ouvrir le répertoire")

    def planningtab__calendar__paint_cells(self):
        """
        Met à jour les jours où des épisodes ont étés vus (colore le fond du jour)

        :return:
        """

        self.planningCalendar.cellsCondition.clear()
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
        selected_date = self.planningCalendar.selectedDate().toPyDate()

        sql_data = {'planning_date': selected_date}
        self.cursor.execute(getDataForTheChoosenDay, sql_data)
        self.planning_watched = self.cursor.fetchall()

        # Affichage du nombre d'épisodes vus pour cette date
        episodes_count = len(self.planning_watched)
        if episodes_count < 2:
            text = "épisode vu"
        else:
            text = "épisodes vus"

        message = "{0} {1}".format(episodes_count, text)

        # Application du message
        self.label_37.setText(message)

        # Remplissage de la liste des séries vues (si elle n'est pas vide)
        if self.planning_watched:

            # Définition de la taille du tableau
            row_number = len(self.planning_watched)
            self.tableWidget_2.setRowCount(row_number)

            # Ajout des éléments
            for index, row in enumerate(self.planning_watched):
                # On affiche pas la colonne de la date
                # Récupération des informations

                serieTitle = row["serie_title"]
                season_title = row["season_title"]
                planning_episode_id = str(row["planning_episode_id"])

                # Ajout des colonnes dans le tableau
                column0 = QTableWidgetItem(serieTitle)
                self.tableWidget_2.setItem(index, 0, column0)

                column1 = QTableWidgetItem(season_title)
                self.tableWidget_2.setItem(index, 1, column1)

                column2 = QTableWidgetItem(planning_episode_id)
                self.tableWidget_2.setItem(index, 2, column2)

        # Taille de cellules s'adaptant au contenu
        self.tableWidget_2.resizeColumnsToContents()

    def planningtab__watched__add(self):
        """Fonction qui ajoute l'épisode à voir dans la liste des épisodes vus"""

        # Récupération de l'identifiant sélectionné
        planningtab_next_index = self.tableWidget_3.currentRow()

        if planningtab_next_index != -1:

            # Récupération de la date sélectionnée
            selected_date = self.planningCalendar.selectedDate().toPyDate()

            # Récupération des informations sur l'élement sélectionné
            data = self.planningToWatch[planningtab_next_index]
            serie_id = data["serie_id"]
            season_id = data["season_id"]
            season_episodes = data["season_episodes"]
            season_watched_episodes = data["season_watched_episodes"]
            season_current_episode_id = season_watched_episodes + 1

            # Commande SQL d'insertion dans les animés vus
            sql_data = {'selected_date': selected_date, 'serie_id': serie_id, 'season_id': season_id,
                        'season_current_episode_id': season_current_episode_id}
            self.cursor.execute(planningAddEpisodeToWatchedList, sql_data)

            # Incrémentation du nombre d'épisodes vus pour la saison
            # Si la saison est terminée, alors
            if season_current_episode_id == season_episodes:

                # On passe le nombre d'épisodes vus à 0
                sql_data = {'season_id': season_id}
                self.cursor.execute(planningSetCurrentEpisodeTo0, sql_data)

                # On incrémente le nombre de visionnages
                self.cursor.execute(planningIncrementSeasonViewCount, sql_data)

                # On passe l'état de la série à 3: terminé
                self.cursor.execute(planningSetSeasonToFinished, sql_data)

            # Sinon on incrémente normalement
            else:
                sql_data = {'season_watched_episodes': season_current_episode_id, 'season_id': season_id}
                self.cursor.execute(planningIncrementEpisode, sql_data)

            # Mise à jour des couleurs de fond des jours dans le calendrier
            self.planningtab__calendar__paint_cells()

            # Mise à jour de la liste des épisodes vus
            self.planningtab__watched__fill()

            # Mise à jour de la liste des épisodes à voir
            self.planningtab__next__fill()

    def planningtab__watched__remove(self):
        """Fonction qui supprime une série dans la liste"""

        # Récupération de l'identifiant de la ligne sélectionnée
        current_id = self.tableWidget_2.currentRow()

        if current_id != -1:
            data = self.planning_watched[current_id]
            planning_id = data["planning_id"]

            sql_data = {'planning_id': planning_id}
            self.cursor.execute(planningRemoveEpisodeFromWatchedList, sql_data)

            # Mise à jour des couleurs de fond des jours dans le calendrier
            self.planningtab__calendar__paint_cells()

            # Mise à jour de la liste des épisodes vus
            self.planningtab__watched__fill()

    def planningtab__is_button_need_to_be_enabled(self):
        """Affiche ou masque le bouton d'ouverture si le dossier de la série n'existe pas"""

        planningtab_next_index = self.tableWidget_3.currentRow()
        if planningtab_next_index != -1:
            # Récupération des informations sur l'élement sélectionné
            data = self.planningToWatch[planningtab_next_index]
            serie_path = data["serie_path"]

            if os.path.exists(serie_path):
                self.pushButton_13.setEnabled(True)
            else:
                self.pushButton_13.setEnabled(False)

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
            sql_query = planningFillWithWatchingSeries

        else:
            # Commande SQL
            sql_query = planningEpisodesFillWithAll

        self.cursor.execute(sql_query)
        self.planningToWatch = self.cursor.fetchall()

        # Remplissage de la liste des séries vues (si elle n'est pas vide)
        if self.planningToWatch:

            # Définition de la taille du tableau
            row_number = len(self.planningToWatch)
            self.tableWidget_3.setRowCount(row_number)

            # Ajout des éléments
            for index, row in enumerate(self.planningToWatch):
                # Récupération des informations
                serie_title = row["serie_title"]
                season_title = row["season_title"]
                planning_episode_id = row["season_watched_episodes"]  # Identifiant du prochain épisode
                planning_episode_id_next = row["season_watched_episodes"] + 1
                planning_episodes = row["season_episodes"]
                plannning_episode_id_total = "{} / {}".format(planning_episode_id_next, planning_episodes)

                # Ajout des colonnes dans le tableau
                column0 = QTableWidgetItem(serie_title)
                self.tableWidget_3.setItem(index, 0, column0)

                column1 = QTableWidgetItem(season_title)
                self.tableWidget_3.setItem(index, 1, column1)

                column2 = QTableWidgetItem(plannning_episode_id_total)
                self.tableWidget_3.setItem(index, 2, column2)

                progress_bar = QProgressBar(self)
                progress_bar.setMinimum(0)
                progress_bar.setMaximum(planning_episodes)
                progress_bar.setValue(
                    planning_episode_id)  # Car si un film donc épisode 1 / 1 on à déja une barre à 100%

                # Style différent si on est sous Windows
                if platform.system() == "Windows":
                    progress_bar.setStyleSheet("QProgressBar::chunk ""{""background-color: #2B65EC;""}")
                    progress_bar.setAlignment(Qt.AlignCenter)

                self.tableWidget_3.setCellWidget(index, 3, progress_bar)

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
        planningtab_next_index = self.tableWidget_3.currentRow()

        if planningtab_next_index != -1:

            # Récupération des informations sur l'élement sélectionné
            data = self.planningToWatch[planningtab_next_index]
            serie_path = data["serie_path"]

            if serie_path:
                if not open_file_explorer(serie_path):
                    print("Impossible d'ouvrir le répertoire")

    def planningtab__on_season_dates_state_changed(self):

        # Si aucune saison n'est selectionnée, alors on sort, pas besoin d'afficher quoi que ce soit
        planningtab_season_index = self.tableWidget_3.currentRow()
        if planningtab_season_index == -1:
            self.season_dates_checkbox.setCheckState(False)
            return

        checked = self.season_dates_checkbox.isChecked()
        enabled = not checked

        self.planningCalendar.setEnabled(enabled)
        self.pushButton_9.setEnabled(enabled)
        self.planningAddButton.setEnabled(enabled)
        self.planningDeleteButton.setEnabled(enabled)
        self.checkBox.setEnabled(enabled)
        self.label_10.setEnabled(enabled)
        self.label_37.setEnabled(enabled)

        self.tableWidget_2.setRowCount(0)

        # Si on veut voir la liste normale
        if not checked:
            # Changement du nom des colonnes
            self.tableWidget_2.setHorizontalHeaderLabels(["Série", "Saison", "Episode"])
            self.planningtab__watched__fill()

        else:
            # Changement du nom des colonnes
            self.tableWidget_2.setHorizontalHeaderLabels(["Date", "Delta", "Episode(s)"])
            self.planningtab__list_season_dates()

    def planningtab__list_season_dates(self):
        # Récupération de l'identifiant sélectionné
        planningtab_season_index = self.tableWidget_3.currentRow()

        if planningtab_season_index != -1:
            # Récupération des informations sur l'élement sélectionné
            data = self.planningToWatch[planningtab_season_index]
            season_id = data["season_id"]

            sql_data = {'season_id': season_id}
            self.cursor.execute(getDatesListForSeasonId, sql_data)
            results = self.cursor.fetchall()

            # Remplissage de la liste des séries vues (si elle n'est pas vide)
            if results:
                # Définition de la taille du tableau
                results_number = len(results)
                self.tableWidget_2.setRowCount(results_number)

                # Ajout des éléments
                old_date_object = None
                for index, row in enumerate(results):
                    # On affiche pas la colonne de la date
                    # Récupération des informations

                    date_object = datetime.strptime(row["planning_date"], "%Y-%m-%d")
                    date_french = date_object.strftime("%d/%m/%Y")
                    date = date_object.strftime("%d %B %Y")

                    # Calcule le delta du nombre de jours entre l'épisode actuel et le précédent.

                    if old_date_object:
                        time_delta = date_object - old_date_object
                        days = time_delta.days

                        if days == 0:
                            date_delta_message = ""
                        else:
                            date_delta_message = "⮩{} jours".format(days)

                    else:
                        date_delta_message = ""

                    old_date_object = date_object

                    episode_id = str(row["episodes"])

                    column0 = QTableWidgetItem(date_french)
                    self.tableWidget_2.setItem(index, 0, column0)

                    column1 = QTableWidgetItem(date_delta_message)
                    self.tableWidget_2.setItem(index, 1, column1)

                    column2 = QTableWidgetItem(episode_id)
                    self.tableWidget_2.setItem(index, 2, column2)

            # Taille de cellules s'adaptant au contenu
            self.tableWidget_2.resizeColumnsToContents()

    def fulllisttab_table_fill(self):
        self.full_list_table.setRowCount(0)

        today_date_object = datetime.now()

        self.cursor.execute(getFullSeriesList)
        results = self.cursor.fetchall()

        self.label_40.setText("Nombre d'éléments: " + str(len(results)))
        self.full_list_table.setRowCount(len(results))

        for index, row in enumerate(results):
            ids = "{} - {}".format(row["serie_sort_id"], row["season_sort_id"])
            column0 = QTableWidgetItem(ids)
            self.full_list_table.setItem(index, 0, column0)

            column1 = QTableWidgetItem(row["serie_title"])
            self.full_list_table.setItem(index, 1, column1)

            column2 = QTableWidgetItem(row["season_title"])
            self.full_list_table.setItem(index, 2, column2)

            column3 = QTableWidgetItem(str(row["season_episodes"]))
            self.full_list_table.setItem(index, 3, column3)

            # Pour les années et l'age
            if not row["season_release_year"] or row["season_release_year"] == "None":
                release_year = ""
                age = ""

            else:
                release_year = str(row["season_release_year"])
                # TODO: Dans une prochaine version, indiquer dans la BDD le type ede date enregistré
                # On verifie si on à seulement une année
                if len(release_year) == 4:
                    # Différence entre deux dates
                    release_year_datetime_object = datetime.strptime(release_year, "%Y")
                    age_diff = today_date_object.year - release_year_datetime_object.year
                    age = "{} ans".format(age_diff)
                else:
                    age = ""

            column4 = QTableWidgetItem(release_year)
            self.full_list_table.setItem(index, 4, column4)

            column5 = QTableWidgetItem(age)
            self.full_list_table.setItem(index, 5, column5)

            state_id = row["season_state"]
            column6 = QTableWidgetItem(self.seasonStates[state_id])
            self.full_list_table.setItem(index, 6, column6)

            column7 = QTableWidgetItem(str(row["season_view_count"]))
            self.full_list_table.setItem(index, 7, column6)

        #self.full_list_table.resizeColumnsToContents()

    def stats__fill(self):

        # Remplissage des données sur le nombre de séries et de saisons
        # Au lieu d'avoir 3 lignes poure chaque requète, on à une boucle for qui associe les donnees aux bon élements
        data_mapper = [(getCountSeasonsStateIndefinie, self.label_51), (getCountSeasonsStateAVoir, self.label_46),
                       (getCountSeasonsStateEnCours, self.label_45), (getCountSeasonsStateTerminee, self.label_44),
                       (getCountSeasonsAStatebandonnee, self.label_48),
                       (getCountSeasons, self.label_64), (getCountSeries, self.label_67)]

        for data in data_mapper:
            query = data[0]
            widget_name = data[1]

            self.cursor.execute(query)
            value = str(self.cursor.fetchone()["nb_elements"])
            widget_name.setText(value)

    def notestab__fill(self):
        """Fonction qui rempli les notes"""

        self.cursor.execute(notesGet)

        notes = self.cursor.fetchone()

        # Si il y a une notes existantes:
        if notes:
            notes_page_id = notes["notes_page_id"]
            notes_data = notes["notes_data"]

            self.plainTextEdit.setPlainText(notes_data)

    def notestab__save(self):
        """Fonction qui sauvegarde les notes"""

        # Récupération des données
        notes_data = self.plainTextEdit.toPlainText()

        # Enregistrement des notes dans la base de données
        sql_data = {'notes_data': notes_data}
        self.cursor.execute(notesSave, sql_data)

    def export_seasons_list(self):
        self.cursor.execute(getFullSeriesList)
        results = self.cursor.fetchall()

        # Création du dossier s'il n'existe pas
        output_folderpath = os.path.join(self.appDataFolder, "output")
        if not os.path.exists(output_folderpath):
            os.makedirs(output_folderpath)

        export_type = "csv"
        if export_type:

            output_filepath = os.path.join(output_folderpath, "Liste des séries.csv")
            with open(output_filepath, 'w', newline='') as csv_file:

                csv_writer = csv.writer(csv_file, delimiter=";")

                # Entetes
                csv_writer.writerow(["Animé", "(Saga / Série)"])

                for index, row in enumerate(results):

                    serie_title = str(row[1])
                    season_title = str(row[3])

                    # Si la saison n'a pas de titre, on reprends celui de la série
                    if season_title in ["", None]:
                        season_title = serie_title

                    row_data = [season_title, serie_title]
                    csv_writer.writerow(row_data)

            # Affiche la fenetre de dialogue d'enregistrement
            extraction_ask = QMessageBox.question(self, 'Extraction terminée', "Extraction terminée !",
                                                  QMessageBox.Close, QMessageBox.Open)

            # Si on clique sur Oui (Sauvegarder)
            if extraction_ask == QMessageBox.Open:
                open_file_explorer(output_folderpath)

    def settings__load(self):
        """Fonction qui charge les paramètres depuis le fichier de configuration"""

        # Si le fichier de paramètres existe
        if os.path.exists(os.path.join(self.appDataFolder, "settings.json")):

            # Ouverture du fichier json
            with open(os.path.join(self.appDataFolder, "settings.json"), "r") as settingsFile:

                # Chargement avec la bibliotheque JSON
                self.settings = load(settingsFile)

        else:
            # Utilisation des paramètres par défaut
            self.settings = self.defaultSettings

            # Création d'un fichier de configuration
            self.settings__save()

    def settings__fill(self):
        """Fonction qui rempli les parametres dans l'onglet associé"""

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
            # Sauvegarde des paramètres avec JSON
            dump(self.settings, settingsFile)

        self.statusbar.showMessage("Paramètres sauvegardés. Relancer l'application pour qu'ils prennent effet.")

    def fill_about_data(self):
        self.label_70.setText(self.app_version)
        self.label_75.setText(platform.python_version())
        self.label_72.setText(QT_VERSION_STR)
        self.label_74.setText(PYQT_VERSION_STR)

    # Fonctions de l'onglet outils
    def tools__watch_time__execute(self):
        """Fonction qui permet d'établir un planning """

        # Effacement de la liste
        self.listWidget_2.clear()

        # Récupération du contenu des spinbox
        episode_number = self.spinBox_2.value()
        episode_length = self.spinBox_3.value()

        # Récupération de l'heure de départ à partir de la textbox  et la convertion en string
        start_string = str(self.timeEdit.dateTime().toString("hh:mm"))  # time().toPyTime()

        # Convertion de la chaine en type datetime
        start = datetime.strptime(start_string, "%H:%M")

        for x in range(episode_number):
            end = start + timedelta(minutes=episode_length)
            row_text = "{:02d} - {:02d}:{:02d} -> {:02d}:{:02d}".format(x + 1, start.hour, start.minute, end.hour,
                                                                        end.minute)  # Chaine qui sera affichée

            # Création de l'élément
            row = QListWidgetItem(row_text)

            # Ajout de l'élément dans le tableau
            self.listWidget_2.addItem(row)

            # Décale la plage
            start = end

    def tools__watch_time__local_time(self):
        """Fonction qui permet de choisir l'heure actuelle dans l'outil"""

        # Récupération de l'heure locale
        local_time = QTime.currentTime()

        # Application de l'heure sur l'objet timeEdit
        self.timeEdit.setTime(local_time)

    def on_close(self, event):
        """Action appelée à la fermeture de l'application"""

        # Si il y a eu des modifications
        if self.database.total_changes > 0:

            # Affiche la fenetre de dialogue d'enregistrement
            save_question = QMessageBox.question(self, 'Enregistrer les changements', "Enregistrer les modifications ?",
                                                 QMessageBox.Yes, QMessageBox.No)

            # Si on clique sur Oui (Sauvegarder)
            if save_question == QMessageBox.Yes:
                # Enregistre les modifications dans la bdd
                self.database.commit()

            # Si on clique sur Quitter sans sauvegarder
            elif save_question == QMessageBox.No:

                # Annule tout les changements depuis le dernier enregistrement
                self.database.rollback()
