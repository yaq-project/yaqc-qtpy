from qtpy import QtWidgets, QtCore
import qtypes
import yaqc

from ._properties_table_widget import PropertiesTableWidget


class CardWidget(QtWidgets.QWidget):

    def __init__(self, qclient):
        super().__init__()
        self.qclient = qclient
        self.box = QtWidgets.QVBoxLayout()
        self.box.setContentsMargins(0, 0, 0, 0)
        self.table = qtypes.widgets.InputTable()
        self.table.append(None, f"{qclient.host}:{qclient.port}")
        self.box.addWidget(self.table)
        self._set_table()
        self._properties_table_widget = PropertiesTableWidget(qclient=qclient)
        self.box.addWidget(self._properties_table_widget)
        self.setLayout(self.box)

    def _on_busy_signal(self, busy):
        self.busy.set(busy)

    def _set_table(self):
        # name
        name = qtypes.String(disabled=True)
        name.set(self.qclient.id()["name"])
        self.table.append(name, "name")
        # busy
        self.busy = qtypes.Bool(disabled=True)
        self.table.append(self.busy, "busy")
        self.qclient.busy_signal.connect(self._on_busy_signal)
