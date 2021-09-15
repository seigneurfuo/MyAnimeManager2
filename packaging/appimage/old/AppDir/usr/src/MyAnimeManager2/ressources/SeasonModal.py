from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
import os


class SeasonModal(QDialog):
    def __init__(self, parent, action, serie_id, season_data):
        """Classe de la fenetre modale seasonModal"""

        super(SeasonModal, self).__init__()

        self.parent = parent
        self.action = action
        self.serieId = serie_id
        self.seasonData = season_data

        loadUi(os.path.join(self.parent.appDir, 'ressources/SeasonModal.ui'), self)

        # Définition des évenements de la fenetre
        self.events()

    def events(self):
        """Evènements de la fenetre modale"""

        # Evenement du bouton retour (Annuler)
        self.cancelButton.clicked.connect(self.oncancel)
        self.saveButton.clicked.connect(self.save)

        # venements en mode édition
        if self.action == "edit":
            self.fill()

    def fill(self):
        """Fonction qui rempli les informations lors de l'édition d'une saison"""

        # Récupération des informations
        season_data = self.seasonData
        season_sort_id = season_data["season_sort_id"]
        season_title = str(season_data["season_title"])
        season_studio = str(season_data["season_studio"])
        season_description = str(season_data["season_description"])
        season_release_year = str(season_data["season_release_year"])
        season_fansub_team = str(season_data["season_fansub_team"])
        season_episodes = season_data["season_episodes"]
        season_watched_episodes = season_data["season_watched_episodes"]
        season_view_count = season_data["season_view_count"]
        season_language = season_data["season_language"]
        season_state = season_data["season_state"]
        season_notes = season_data["season_notes"]

        # Application des informations sur l'interface
        self.spinBox_2.setValue(season_sort_id)
        self.lineEdit.setText(season_studio)
        self.lineEdit_2.setText(season_title)
        self.lineEdit_3.setText(season_description)
        self.lineEdit_5.setText(season_release_year)
        self.lineEdit_6.setText(season_fansub_team)
        self.episodesSpinbox.setValue(season_episodes)
        self.episodesWatchedSpinbox.setValue(season_watched_episodes)
        self.seasonViewCountSpinbox.setValue(season_view_count)
        self.seasonLanguageComboBox.setCurrentIndex(season_language)
        self.seasonStateComboBox.setCurrentIndex(season_state)
        self.textEdit.setText(season_notes)

    def save(self):
        """Fonction appelée lors du clic sur le bouton enregistrer"""

        # Récupération de l'identifiant de la série
        serie_id = self.serieId

        # Récupération des informations entrées par l'utilisateur
        season_sort_id = self.spinBox_2.text()
        season_title = str(self.lineEdit_2.text())
        season_description = str(self.lineEdit_3.text())
        season_studio = str(self.lineEdit.text())
        season_release_year = self.lineEdit_5.text()
        season_fansub_team = str(self.lineEdit_6.text())
        season_episodes = self.episodesSpinbox.value()
        season_watched_episodes = self.episodesWatchedSpinbox.value()
        season_language = self.seasonLanguageComboBox.currentIndex()
        season_view_count = self.seasonViewCountSpinbox.value()
        season_state = self.seasonStateComboBox.currentIndex()
        season_notes = self.textEdit.toPlainText()

        # Vérification des informations avant traitement
        if season_release_year == "":
            season_release_year = None

        if self.action == "create":
            # Commande SQL de création # seriedId a terminer
            sql_query = """INSERT INTO season (season_id, season_sort_id, season_title, season_description, season_studio, season_release_year, season_episodes, season_watched_episodes, season_fk_serie_id, season_language, season_state, season_fansub_team, season_view_count, season_notes)
                          VALUES (NULL, :season_sort_id, :season_title, :season_description, :season_studio, :season_release_year, :season_episodes, :season_watched_episodes, :serie_id, :season_language, :season_state, :season_fansub_team, :season_view_count, :season_notes)"""

            sql_data = {'season_sort_id': season_sort_id, 'season_title': season_title,
                        'season_description': season_description,
                        'season_studio': season_studio, 'season_release_year': season_release_year,
                        'season_episodes': season_episodes, 'season_watched_episodes': season_watched_episodes,
                        'serie_id': serie_id, 'season_language': season_language, 'season_state': season_state,
                        'season_fansub_team': season_fansub_team,
                        'season_view_count': season_view_count, 'season_notes': season_notes}

            # Execution de la requete SQL
            self.parent.cursor.execute(sql_query, sql_data)


        elif self.action == "edit":
            # Récupération des informations sur la saison
            season_data = self.seasonData
            season_id = int(season_data["season_id"])

            # Commande SQL de mise à jour
            sql_query = """
            UPDATE season
            SET season_sort_id = :season_sort_id,
            season_title = :season_title,
            season_description = :season_description,
            season_studio = :season_studio,
            season_release_year = :season_release_year,
            season_episodes = :season_episodes,
            season_fansub_team = :season_fansub_team,
            season_watched_episodes = :season_watched_episodes,
            season_view_count = :season_view_count,
            season_language = :season_language,
            season_state = :season_state,
            season_notes = :season_notes
            WHERE season_id = :season_id"""

            sql_data = {'season_sort_id': season_sort_id, 'season_title': season_title,
                        'season_description': season_description,
                        'season_studio': season_studio, 'season_release_year': season_release_year,
                        'season_episodes': season_episodes, 'season_watched_episodes': season_watched_episodes,
                        'season_language': season_language,
                        'season_state': season_state, 'season_id': season_id, 'season_fansub_team': season_fansub_team,
                        'season_view_count': season_view_count, 'season_notes': season_notes}

            # Execution de la requete SQL
            self.parent.cursor.execute(sql_query, sql_data)

        # Mise a jour de informations de la serie (le nombre de saisons change mais il est mis à jour par seasonlist)
        self.parent.listtab__seasonslist__fill()
        self.parent.listtab__seasondata__fill()

        # Fermeture de la fenetre modale
        self.close()

    def oncancel(self):
        """Fonction appelée lors du clic sur le bouton annuler"""

        # Fermeture de la fenetre
        self.close()
