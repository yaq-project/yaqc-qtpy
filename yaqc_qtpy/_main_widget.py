from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np

from ._fields_table_widget import FieldsTableWidget
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
        self._position_buffer = np.full(100, np.nan)
        self._ymin = -1e-6
        self._ymax = 1e-6

    def _create_main_frame(self):
        hbox = QtWidgets.QHBoxLayout()
        # plot
        self.plot_widget = Plot1D()
        self._scatter = self.plot_widget.add_scatter()
        hbox.addWidget(self.plot_widget)
        # right hand scroll area
        self.scroll_area = qtypes.widgets.ScrollArea()
        self.table = qtypes.widgets.InputTable()
        self.table.append(None, f"{self.host}:{self.port}")
        self.scroll_area.add_widget(self.table)
        self._fields_table_widget = FieldsTableWidget(self.host, self.port, verbose=True)
        self.scroll_area.add_widget(self._fields_table_widget)
        hbox.addWidget(self.scroll_area)
        # finish
        self.setLayout(hbox)

    def _set_table(self):
        # id ---
        self.table.append(None, "id")
        # name
        name = qtypes.String(disabled=True)
        name.set(self.client.id()["name"])
        self.table.append(name, "name")
        # kind
        kind = qtypes.String(disabled=True)
        kind.set(self.client.id()["kind"])
        self.table.append(kind, "kind")
        # make
        make = qtypes.String(disabled=True)
        make.set(self.client.id()["make"])
        self.table.append(make, "make")
        # model
        model = qtypes.String(disabled=True)
        model.set(self.client.id()["model"])
        self.table.append(model, "model")
        # serial
        serial = qtypes.String(disabled=True)
        serial.set(self.client.id()["serial"])
        self.table.append(serial, "serial")
        # busy
        self.busy = qtypes.Bool(disabled=True)
        self.busy.set(self.client.busy())
        self.table.append(self.busy, "busy")
        # traits
        if "has-position" in self.client.traits:
            self.position = qtypes.Number()

    def poll(self):
        self.busy.set(self.client.busy())
        self._fields_table_widget.poll()
        self._position_buffer[-1] = self.client.get_position()
        self._ymin = np.nanmin([np.nanmin(self._position_buffer), self._ymin])
        self._ymax = np.nanmax([np.nanmax(self._position_buffer), self._ymax])
        self._scatter.setData(np.arange(100), self._position_buffer)
        self.plot_widget.set_ylim(self._ymin, self._ymax)
        self._position_buffer = np.roll(self._position_buffer, -1)
