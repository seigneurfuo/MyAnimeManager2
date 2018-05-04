from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
import os


class SeasonModal(QDialog):
    def __init__(self, parent, action, serieId, seasonData):
        """Classe de la fenetre modale seasonModal"""

        super(SeasonModal, self).__init__()

        self.parent = parent
        self.action = action
        self.serieId = serieId
        self.seasonData = seasonData

        loadUi(os.path.join(self.parent.appDir, 'ressources/SeasonModal.ui'), self)

        # Définition des évenements de la fenetre
        self.events()

    def events(self):
        """Evènements de la fenetre modale"""

        # Evenement du bouton retour (Annuler)
        self.cancelButton.clicked.connect(self.oncancel)
        self.saveButton.clicked.connect(self.save)

        # venements en mode édition
        if self.action == "edit": self.fill()

    def fill(self):
        """Fonction qui rempli les informations lors de l'édition d'une saison"""

        # Récupération des informations
        seasonData = self.seasonData
        seasonSortId = seasonData["seasonSortId"]
        seasonTitle = str(seasonData["seasonTitle"])
        seasonStudio = str(seasonData["seasonStudio"])
        seasonDescription = str(seasonData["seasonDescription"])
        seasonReleaseYear = str(seasonData["seasonReleaseYear"])
        seasonFansubTeam = str(seasonData["seasonFansubTeam"])
        seasonEpisodes = seasonData["seasonEpisodes"]
        seasonWatchedEpisodes = seasonData["seasonWatchedEpisodes"]
        seasonViewCount = seasonData["seasonViewCount"]
        seasonState = seasonData["seasonState"]
        seasonNotes = seasonData["seasonNotes"]

        # Application des informations sur l'interface
        self.spinBox_2.setValue(seasonSortId)
        self.lineEdit.setText(seasonStudio)
        self.lineEdit_2.setText(seasonTitle)
        self.lineEdit_3.setText(seasonDescription)
        self.lineEdit_5.setText(seasonReleaseYear)
        self.lineEdit_6.setText(seasonFansubTeam)
        self.episodesSpinbox.setValue(seasonEpisodes)
        self.episodesWatchedSpinbox.setValue(seasonWatchedEpisodes)
        self.seasonViewCountSpinbox.setValue(seasonViewCount)
        self.seasonStateComboBox.setCurrentIndex(seasonState)
        self.textEdit.setText(seasonNotes)

    def save(self):
        """Fonction appelée lors du clic sur le bouton enregistrer"""

        # Récupération de l'identifiant de la série
        serieId = self.serieId

        # Récupération des informations entrées par l'utilisateur
        seasonSortId = self.spinBox_2.text()
        seasonTitle = str(self.lineEdit_2.text())
        seasonDescription = str(self.lineEdit_3.text())
        seasonStudio = str(self.lineEdit.text())
        seasonReleaseYear = self.lineEdit_5.text()
        seasonFansubTeam = str(self.lineEdit_6.text())
        seasonEpisodes = self.episodesSpinbox.value()
        seasonWatchedEpisodes = self.episodesWatchedSpinbox.value()
        seasonViewCount = self.seasonViewCountSpinbox.value()
        seasonState = self.seasonStateComboBox.currentIndex()
        seasonNotes = self.textEdit.toPlainText()

        # Vérification des informations avant traitement
        if seasonReleaseYear == "": seasonReleaseYear = None

        if self.action == "create":
            # Commande SQL de création # seriedId a terminer
            sqlQuery = """INSERT INTO season (seasonId, seasonSortId, seasonTitle, seasonDescription, seasonStudio, seasonReleaseYear, seasonEpisodes, seasonWatchedEpisodes, seasonFKserieId, seasonState, seasonFansubTeam, seasonViewCount, seasonNotes)
                          VALUES (NULL, :seasonSortId, :seasonTitle, :seasonDescription, :seasonStudio, :seasonReleaseYear, :seasonEpisodes, :seasonWatchedEpisodes, :serieId, :seasonState, :seasonFansubTeam, :seasonViewCount, :seasonNotes)"""

            sqlData = {'seasonSortId': seasonSortId, 'seasonTitle': seasonTitle, 'seasonDescription': seasonDescription,
                       'seasonStudio': seasonStudio, 'seasonReleaseYear': seasonReleaseYear,
                       'seasonEpisodes': seasonEpisodes, 'seasonWatchedEpisodes': seasonWatchedEpisodes,
                       'serieId': serieId, 'seasonState': seasonState, 'seasonFansubTeam': seasonFansubTeam,
                       'seasonViewCount': seasonViewCount, 'seasonNotes': seasonNotes}

            # Execution de la requete SQL
            self.parent.cursor.execute(sqlQuery, sqlData)


        elif self.action == "edit":
            # Récupération des informations sur la saison
            seasonData = self.seasonData
            seasonId = int(seasonData["seasonId"])

            # Commande SQL de mise à jour
            sqlQuery = """
            UPDATE season
            SET seasonSortId = :seasonSortId,
            seasonTitle = :seasonTitle,
            seasonDescription = :seasonDescription,
            seasonStudio = :seasonStudio,
            seasonReleaseYear = :seasonReleaseYear,
            seasonEpisodes = :seasonEpisodes,
            seasonFansubTeam = :seasonFansubTeam,
            seasonWatchedEpisodes = :seasonWatchedEpisodes,
            seasonViewCount = :seasonViewCount,
            seasonState = :seasonState,
            seasonNotes = :seasonNotes
            WHERE seasonId = :seasonId"""

            sqlData = {'seasonSortId': seasonSortId, 'seasonTitle': seasonTitle, 'seasonDescription': seasonDescription,
                       'seasonStudio': seasonStudio, 'seasonReleaseYear': seasonReleaseYear,
                       'seasonEpisodes': seasonEpisodes, 'seasonWatchedEpisodes': seasonWatchedEpisodes,
                       'seasonState': seasonState, 'seasonId': seasonId, 'seasonFansubTeam': seasonFansubTeam,
                       'seasonViewCount': seasonViewCount, 'seasonNotes': seasonNotes}

            # Execution de la requete SQL
            self.parent.cursor.execute(sqlQuery, sqlData)

        # Mise a jour de informations de la serie (le nombre de saisons change mais il est mis à jour par seasonlist)
        self.parent.listtab__seasonslist__fill()
        self.parent.listtab__seasondata__fill()

        # Fermeture de la fenetre modale
        self.close()

    def oncancel(self):
        """Fonction appelée lors du clic sur le bouton annuler"""

        # Fermeture de la fenetre
        self.close()
