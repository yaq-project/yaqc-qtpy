from qtpy import QtWidgets, QtCore
import qtypes
import yaqc

from ._plot import Plot1D


class MainWidget(QtWidgets.QWidget):

    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        try:
            self.client = yaqc.Client(host=host, port=port)
        except Exception as e:
            print(e)
        self._create_main_frame()
        self._set_table()

    def _create_main_frame(self):
        hbox = QtWidgets.QHBoxLayout()
        # plot
        self.plot_widget = Plot1D()
        hbox.addWidget(self.plot_widget)
        # right hand scroll area
        box = QtWidgets.QVBoxLayout()
        self.scroll_area = qtypes.widgets.ScrollArea()
        box.addWidget(self.scroll_area)
        self.table = qtypes.widgets.InputTable()
        self.table.append(None, f"{self.host}:{self.port}")
        self.scroll_area.add_widget(self.table)
        hbox.addLayout(box)
        # finish
        self.setLayout(hbox)

    def _set_table(self):
        # id ---
        self.table.append(None, "id")
        # name
        name = qtypes.String()
        name.set(self.client.id()["name"])
        self.table.append(name, "name")
        # kind
        kind = qtypes.String()
        kind.set(self.client.id()["kind"])
        self.table.append(kind, "kind")
        # make
        make = qtypes.String()
        make.set(self.client.id()["make"])
        self.table.append(make, "make")
        # model
        model = qtypes.String()
        model.set(self.client.id()["model"])
        self.table.append(model, "model")
        # serial
        serial = qtypes.String()
        serial.set(self.client.id()["serial"])
        self.table.append(serial, "serial")
        # busy
        self.busy = qtypes.Bool()
        self.busy.set(self.client.busy())
        self.table.append(self.busy, "busy")
        # fields
        if len(self.client._protocol.get("fields", {})) > 0:
            self.table.append(None, "fields")
            for k, d in self.client._protocol["fields"].items():
                self.table.append(qtypes.Number(), k)
        # traits
        if "has-position" in self.client.traits:
            self.position = qtypes.Number()

    def poll(self):
        pass
