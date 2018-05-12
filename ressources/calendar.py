from PyQt5.QtWidgets import QCalendarWidget

class Calendar(QCalendarWidget):
    """
    Une classe personalisée qui permet d'étendre les possibilités du calendrier
    Found on: https://stackoverflow.com/questions/19083140/custom-calendar-cell-in-pyqt
    """

    def __init__(self, parent=None):
        """

        :param parent:
        """

        QCalendarWidget.__init__(self, parent)
        self.cellBackgroundColor = None
        self.cellsCondition = []

    def setCellsBackgroundColor(self, color):
        """
        Une méthode qui permet de choisir la couleur de fond d'une cellule

        :param color:
        :return:
        """

        self.cellBackgroundColor = color

    def paintCell(self, painter, rect, date):
        QCalendarWidget.paintCell(self, painter, rect, date)

        # Si une couleur à été choisi pour l'arrière plan des cellules, alors on l'applique
        if self.cellBackgroundColor:
            #if self.cellsCondition:

            if date in self.cellsCondition:
                painter.fillRect(rect, self.cellBackgroundColor)