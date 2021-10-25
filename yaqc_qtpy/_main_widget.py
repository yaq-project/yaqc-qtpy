from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np
import entrypoints

from ._properties_table_widget import PropertiesTableWidget
from ._main_by_traits import MainByTraits
from ._plot import Plot1D


class MainWidget(QtWidgets.QTabWidget):

    def __init__(self, qclient):
        super().__init__()
        self.qclient = qclient
        self.addTab(QtWidgets.QLabel("TODO"), "config")
        self.addTab(MainByTraits(qclient=self.qclient), "traits")
        # gui tabs provided via entrypoints
        group = f"yaqc_qtpy.main.{self.qclient._client._protocol['protocol']}"
        for ep in entrypoints.get_group_all(group):
            print(ep)
            self.addTab(ep.load()(client=None), ep.name)
        self.setCurrentIndex(self.count() - 1)

    def poll(self):
        pass
