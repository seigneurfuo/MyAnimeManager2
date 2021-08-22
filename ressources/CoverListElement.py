from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget

from ressources.utils import get_serie_cover


class CoverListElement(QWidget):
    cover_x_size = 128
    cover_y_size = 128


    def __init__(self, parent, data):
        super(QWidget, self).__init__()

        self.parent = parent
        self.data = data

        self.setup_ui()


    def setup_ui(self):
        self.qvboxlayout = QVBoxLayout()

        # Image de cover
        self.cover_filename = get_serie_cover(self.parent.appDir, self.parent.appDataFolder, self.data["serie_id"])
        self.cover_pixmap = QPixmap(self.cover_filename)
        self.cover_label = QLabel()
        self.cover_label.setPixmap(self.cover_pixmap)
        self.cover_label.setFixedSize(self.cover_x_size, self.cover_y_size)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.qvboxlayout.addWidget(self.cover_label)

        # Nom
        serie_name = "{} - {}".format(self.data["serie_sort_id"], self.data["serie_title"])
        self.name_label = QLabel(serie_name)
        self.qvboxlayout.addWidget(self.name_label)

        # Boutton d'édition
        self.edit_button = QPushButton("Editer")
        self.qvboxlayout.addWidget(self.edit_button)

        self.setLayout(self.qvboxlayout)


    def events(self):
        pass