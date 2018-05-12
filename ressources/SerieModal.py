from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi

from shutil import copy
import os
from ressources.log import *


class SerieModal(QDialog):
    def __init__(self, parent, action, serieData):
        """Classe de la fenetre modale seasonModal"""

        super(SerieModal, self).__init__()

        self.parent = parent
        self.action = action
        self.serieData = serieData
        self.seriePath = ""

        loadUi(os.path.join(self.parent.appDir, 'ressources/SerieModal.ui'), self)

        # Définition des évenements de la fenetre
        self.events()


    def events(self):
        """Evènements de la fenetre modale"""

        # Evenement du bouton retour (Annuler)
        self.backButton.clicked.connect(self.cancel)

        # Assigne le bouton de sauvegarde à la fonction de sauvegarde
        self.saveButton.clicked.connect(self.save)

        # Assigne le bouton de recherche de dossier
        self.choosePathButton.clicked.connect(self.choose_path)

        #
        # On a besoin de l'id interne de la série pour nommer la cover. Mais on ne peut pas la connaitre avant la création de la série.
        # On empèche donc l'ajout d'une cover en mode création
        #

        if self.action == "create":

            # Désactivation du texte de sélection de cover
            self.label_13.hide()

            # Désactivation du bouton de sélection de cover
            self.chooseCoverButton.hide()

            # Désactivation de l'image
            self.coverPreview.hide()


        elif self.action == "edit":
            # Bouton de sélection de l'image de la série (par défault lors de la création on ne peut pas choisir l'image: contournement de bug)
            self.chooseCoverButton.clicked.connect(self.choose_cover)

            # Remplissage des informations
            self.fill()


    def choose_cover(self):
        """Fonction qui permet de rechercher une image"""

        # Ouveture d'une fenetre de sélection de fichier
        fileName, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "",
                                                  "Fichiers images (*.jpg *.jpeg *.png *.gif);;Tous les fichiers (*)")

        # Si un fichier à été sélectionné
        if fileName:
            logMsg = "Chargé: {0}".format(fileName)
            log.info(logMsg)

            # Définition du nom de l'image de destination
            serieId = str(self.serieData["serieId"])
            coverFilename = "./profile/covers/{0}".format(serieId)

            # Copie l'image sélectionnée dans le dossier correpondant
            copy(fileName, coverFilename)

            # Application de l'image
            pixmap = QPixmap(coverFilename)
            self.coverPreview.setPixmap(pixmap)


    def choose_path(self):
        """Fonction qui permet à l'utilisateur de choisir le dossier de la série"""

        # Ouveture d'une fenetre de sélection de dossier
        folderName = QFileDialog.getExistingDirectory(self, "Choisir le dossier de la série")

        # Si un dossier à été sélectionné
        if folderName:
            #log.info(folderName)

            # Application du texte sur le widget line edit
            self.lineEdit_2.setText(folderName)


    def save(self):
        """Fonction qui permet d'ajouter une nouvelle série"""

        # Récupération des informations entrées par l'utilisateur
        serieSortId = self.spinBox_2.value()
        serieTitle = str(self.lineEdit.text())
        seriePath = str(self.lineEdit_2.text())  # On récupère le chemin de la série depuis un bloc de texte car il est possible de coller directement le chemin de la série au lieu d'utiliser l'explorateur

        # Checkbox (série appréciée)
        if self.checkBox.isChecked():
            serieLiked = 1
        else:
            serieLiked = 0

        if self.action == "create":

            # Application des modifications dans la base
            sqlQuery = "INSERT INTO serie (serieId, serieSortId, serieTitle, serieLiked, seriePath) VALUES (NULL, :serieSortId, :serieTitle, :serieLiked, :seriePath)"
            sqlData = {'serieSortId': serieSortId, 'serieTitle': serieTitle, 'serieLiked': serieLiked,
                    'seriePath': seriePath}
            self.parent.cursor.execute(sqlQuery, sqlData)

        elif self.action == "edit":

            # Récupération des informations sur la série
            serieData = self.serieData
            serieId = int(serieData["serieId"])

            # Commande SQL de mise à jour
            sqlQuery = "UPDATE serie SET serieSortId = :serieSortId, serieTitle = :serieTitle, serieLiked = :serieLiked, seriePath = :seriePath WHERE serieId = :serieId"
            sqlData = {'serieSortId': serieSortId, 'serieTitle': serieTitle, 'serieLiked': serieLiked,
                    'seriePath': seriePath, 'serieId': serieId}
            self.parent.cursor.execute(sqlQuery, sqlData)

        # Affichage de la commande sql (debug)
        #log.info(sqlQuery)

        # Mise a jour de la liste des séries et des informations
        self.parent.listtab__serieslist__fill()
        self.parent.listtab__seriedata__fill()

        # Fermeture de la fenetre modale
        self.close()


    def fill(self):
        """Fonction qui rempli les informations lors de l'édition d'une série"""

        # Récupération des informations sur la série
        serieData = self.serieData
        serieSortId = int(serieData["serieSortId"])
        serieTitle = str(serieData["serieTitle"])
        serieLiked = int(serieData["serieLiked"])
        seriePath = str(serieData["seriePath"])

        # Application des informations dans les différents élements
        self.spinBox_2.setValue(serieSortId)
        self.lineEdit.setText(serieTitle)
        self.lineEdit_2.setText(seriePath)

        # Checkbox
        if serieLiked == 1: self.checkBox.setChecked(True)

        # Chargement de l'image
        serieId = str(self.serieData["serieId"])
        coverFilename = "./profile/covers/{0}".format(serieId)
        if os.path.exists(coverFilename):
            # Application de l'image
            pixmap = QPixmap(coverFilename)
            self.coverPreview.setPixmap(pixmap)


    def cancel(self):
        """Fonction appelée lors du clic sur le bouton annuler"""

        # Fermeture de la fenetre
        self.close()
