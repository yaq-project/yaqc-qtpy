import random
import pathlib

from qtpy import QtWidgets, QtCore, QtGui


__here__ = pathlib.Path(__file__).parent


class Splash(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        index = str(random.randrange(5)).zfill(3)
        path = str(__here__ / "splash-images" / f"{index}.jpg")
        self.pixmap = QtGui.QPixmap(path)

    def paintEvent(self, event):
        size = self.size()
        painter = QtGui.QPainter(self)
        point = QtCore.QPoint(0, 0)
        scaledPix = self.pixmap.scaled(
            size,
            QtCore.Qt.KeepAspectRatio,
        )
        # start painting the label from left upper corner
        point.setX((size.width() - scaledPix.width()) // 2)
        point.setY((size.height() - scaledPix.height()) // 2)
        painter.drawPixmap(point, scaledPix)
