from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np
import entrypoints

from ._fields_table_widget import FieldsTableWidget
from ._main_by_traits import MainByTraits
from ._plot import Plot1D


class MainWidget(QtWidgets.QTabWidget):

    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        try:
            self.client = yaqc.Client(host=host, port=port)
        except Exception as e:
            print(e)
        #
        self.addTab(QtWidgets.QLabel("TODO"), "config")
        self.addTab(MainByTraits(host, port), "traits")
        # gui tabs provided via entrypoints
        group = f"yaqc_qtpy.main.{self.client._protocol['protocol']}"
        for ep in entrypoints.get_group_all(group):
            print(ep)
            self.addTab(ep.load()(client=None), ep.name)
        self.setCurrentIndex(self.count() - 1)

    def poll(self):
        pass
