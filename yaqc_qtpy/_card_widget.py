from qtpy import QtWidgets, QtCore
import qtypes
import yaqc


class CardWidget(QtWidgets.QWidget):

    def __init__(self, host: str, port: int):
        super().__init__()
        self.box = QtWidgets.QVBoxLayout()
        self.table = qtypes.widgets.InputTable()
        self.table.append(None, f"{host}:{port}")
        self.box.addWidget(self.table)
        try:
            self.client = yaqc.Client(host=host, port=port)
        except Exception as e:
            self.client = None
        self._set_table()
        self.setLayout(self.box)

    def _set_table(self):
        # name
        name = qtypes.String()
        name.set(self.client.id()["name"])
        self.table.append(name, "name")
        # busy
        self.busy = qtypes.Bool()
        self.busy.set(self.client.busy())
        self.table.append(self.busy, "busy")
        # traits
        if "has-position" in self.client.traits:
            self.position = qtypes.Number()
            self.table.append(self.position, "position")

    def poll(self):
        # busy
        #self.busy.set(self.client.busy())
        # traits
        if "has-position" in self.client.traits:
            self.position.set(self.client.get_position())
