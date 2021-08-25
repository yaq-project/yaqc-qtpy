from qtpy import QtWidgets, QtCore
import qtypes
import yaqc

from ._fields_table_widget import FieldsTableWidget


class CardWidget(QtWidgets.QWidget):

    def __init__(self, host: str, port: int):
        super().__init__()
        self.box = QtWidgets.QVBoxLayout()
        self.box.setContentsMargins(0, 0, 0, 0)
        self.table = qtypes.widgets.InputTable()
        self.table.append(None, f"{host}:{port}")
        self.box.addWidget(self.table)
        try:
            self.client = yaqc.Client(host=host, port=port)
        except Exception as e:
            self.client = None
        self._set_table()
        self._fields_table_widget = FieldsTableWidget(host, port)
        self.box.addWidget(self._fields_table_widget)
        self.setLayout(self.box)

    def _set_table(self):
        # name
        name = qtypes.String(disabled=True)
        name.set(self.client.id()["name"])
        self.table.append(name, "name")
        # busy
        self.busy = qtypes.Bool(disabled=True)
        self.busy.set(self.client.busy())
        self.table.append(self.busy, "busy")

    def poll(self):
        self.busy.set(self.client.busy())
        self._fields_table_widget.poll()
