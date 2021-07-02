from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi

from shutil import copy
import os
from ressources.log import *


class SerieModal(QDialog):
    def __init__(self, parent, action, serie_data):
        """Classe de la fenetre modale seasonModal"""

        super(SerieModal, self).__init__()

        self.parent = parent
        self.action = action
        self.serieData = serie_data
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
        # On a besoin de l'id interne de la série pour nommer la cover. Mais on ne peut pas la connaitre avant la
        # création de la série. On empèche donc l'ajout d'une cover en mode création
        #

        if self.action == "create":

            # Désactivation du texte de sélection de cover
            self.label_13.hide()

            # Désactivation du bouton de sélection de cover
            self.chooseCoverButton.hide()

            # Désactivation de l'image
            self.coverPreview.hide()


        elif self.action == "edit":
            # Bouton de sélection de l'image de la série (par défault lors de la création on ne peut pas choisir
            # l'image: contournement de bug)
            self.chooseCoverButton.clicked.connect(self.choose_cover)

            # Remplissage des informations
            self.fill()

    def choose_cover(self):
        """Fonction qui permet de rechercher une image"""

        # Ouveture d'une fenetre de sélection de fichier
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "",
                                                   "Fichiers images (*.jpg *.jpeg *.png *.gif);;Tous les fichiers (*)")

        # Si un fichier à été sélectionné
        if file_name:
            # Définition du nom de l'image de destination
            serie_id = str(self.serieData["serie_id"])
            cover_filename = "./profile/covers/{0}".format(serie_id)

            # Copie l'image sélectionnée dans le dossier correpondant
            copy(file_name, cover_filename)

            # Application de l'image
            pixmap = QPixmap(cover_filename)
            self.coverPreview.setPixmap(pixmap)

    def choose_path(self):
        """Fonction qui permet à l'utilisateur de choisir le dossier de la série"""

        # Ouveture d'une fenetre de sélection de dossier
        folder_name = QFileDialog.getExistingDirectory(self, "Choisir le dossier de la série")

        # Si un dossier à été sélectionné
        if folder_name:
            # Application du texte sur le widget line edit
            self.lineEdit_2.setText(folder_name)

    def save(self):
        """Fonction qui permet d'ajouter une nouvelle série"""

        # Récupération des informations entrées par l'utilisateur
        serie_sort_id = self.spinBox_2.value()
        serie_title = str(self.lineEdit.text())
        serie_path = str(
            self.lineEdit_2.text())  # On récupère le chemin de la série depuis un bloc de texte car il est possible
        # de coller directement le chemin de la série au lieu d'utiliser l'explorateur

        # Checkbox (série appréciée)
        if self.checkBox.isChecked():
            serie_liked = 1
        else:
            serie_liked = 0

        if self.action == "create":

            # Application des modifications dans la base
            sql_query = "INSERT INTO serie (serie_id, serie_sort_id, serie_title, serie_liked, serie_path) VALUES (" \
                        "NULL, :serie_sort_id, :serie_title, :serie_liked, :serie_path) "
            sql_data = {'serie_sort_id': serie_sort_id, 'serie_title': serie_title, 'serie_liked': serie_liked,
                        'serie_path': serie_path}
            self.parent.cursor.execute(sql_query, sql_data)

        elif self.action == "edit":

            # Récupération des informations sur la série
            serie_data = self.serieData
            serie_id = int(serie_data["serie_id"])

            # Commande SQL de mise à jour
            sql_query = "UPDATE serie SET serie_sort_id = :serie_sort_id, serie_title = :serie_title, serie_liked = " \
                        ":serie_liked, serie_path = :serie_path WHERE serie_id = :serie_id "
            sql_data = {'serie_sort_id': serie_sort_id, 'serie_title': serie_title, 'serie_liked': serie_liked,
                        'serie_path': serie_path, 'serie_id': serie_id}
            self.parent.cursor.execute(sql_query, sql_data)

        # Mise a jour de la liste des séries et des informations
        self.parent.listtab__serieslist__fill()
        self.parent.listtab__seriedata__fill()

        # Fermeture de la fenetre modale
        self.close()

    def fill(self):
        """Fonction qui rempli les informations lors de l'édition d'une série"""

        # Récupération des informations sur la série
        serie_data = self.serieData
        serie_sort_id = int(serie_data["serie_sort_id"])
        serie_title = str(serie_data["serie_title"])
        serie_liked = int(serie_data["serie_liked"])
        serie_path = str(serie_data["serie_path"])

        # Application des informations dans les différents élements
        self.spinBox_2.setValue(serie_sort_id)
        self.lineEdit.setText(serie_title)
        self.lineEdit_2.setText(serie_path)

        # Checkbox
        if serie_liked == 1:
            self.checkBox.setChecked(True)

        # Chargement de l'image
        serie_id = str(self.serieData["serie_id"])
        cover_filename = "./profile/covers/{0}".format(serie_id)
        if os.path.exists(cover_filename):
            # Application de l'image
            pixmap = QPixmap(cover_filename)
            self.coverPreview.setPixmap(pixmap)

    def cancel(self):
        """Fonction appelée lors du clic sur le bouton annuler"""

        # Fermeture de la fenetre
        self.close()
