from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np
import entrypoints

from ._config_widget import ConfigWidget
from ._has_position_widget import HasPositionWidget
from ._is_sensor_widget import IsSensorWidget
from ._plot import Plot1D


class MainWidget(QtWidgets.QTabWidget):
    def __init__(self, qclient, *, parent=None):
        super().__init__(parent=parent)
        self.qclient = qclient
        self.addTab(ConfigWidget(qclient=self.qclient, parent=self), "config")
        if "has-position" in self.qclient.traits:
            self.addTab(HasPositionWidget(qclient=self.qclient, parent=self), "has-position")
        if "is-sensor" in self.qclient.traits:
            self.addTab(IsSensorWidget(qclient=self.qclient, parent=self), "is-sensor")
        # gui tabs provided via entrypoints
        group = f"yaqc_qtpy.main.{self.qclient._client._protocol['protocol']}"
        for ep in entrypoints.get_group_all(group):
            print(ep)
            self.addTab(ep.load()(qclient), ep.name)
        self.setCurrentIndex(self.count() - 1)

    def poll(self):
        pass
