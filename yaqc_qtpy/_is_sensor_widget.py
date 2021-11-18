import time

from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np
import yaq_traits

from ._plot import Plot1D
from . import qtype_items


class IsSensorWidget(QtWidgets.QSplitter):
    def __init__(self, qclient, *, parent=None):
        super().__init__(parent=parent)
        self.qclient = qclient
        self.addWidget(QtWidgets.QLabel("IsSensorWidget TODO"))
