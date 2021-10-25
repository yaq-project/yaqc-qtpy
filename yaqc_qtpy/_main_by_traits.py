import time

from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np

from ._properties_table_widget import PropertiesTableWidget
from ._plot import Plot1D


class MainByTraits(QtWidgets.QWidget):

    def __init__(self, qclient, *, parent=None):
        super().__init__(parent=parent)
        self.qclient = qclient
        self._create_main_frame()
        self._set_table()
        # plotting variables
        self._position_buffer = np.full(100, np.nan)
        self._timestamp_buffer = np.full(100, np.nan)
        self._ymin = -1e-6
        self._ymax = 1e-6
        # signals and slots
        if "position" in self.qclient.properties:
            self.qclient.properties.position.updated.connect(self._on_position_updated)

    def _create_main_frame(self):
        hbox = QtWidgets.QHBoxLayout()
        # plot
        self.plot_widget = Plot1D()
        self._scatter = self.plot_widget.add_scatter()
        hbox.addWidget(self.plot_widget)
        # right hand scroll area
        self.scroll_area = qtypes.widgets.ScrollArea()
        self.table = qtypes.widgets.InputTable()
        self.table.append(None, f"{self.qclient.host}:{self.qclient.port}")
        self.scroll_area.add_widget(self.table)
        self._properties_table_widget = PropertiesTableWidget(qclient=self.qclient, verbose=True, parent=self)
        self.scroll_area.add_widget(self._properties_table_widget)
        hbox.addWidget(self.scroll_area)
        # finish
        self.setLayout(hbox)

    def _on_position_updated(self, position):
        # roll over, enter new data
        self._position_buffer = np.roll(self._position_buffer, -1)
        self._timestamp_buffer = np.roll(self._timestamp_buffer, -1)
        self._position_buffer[-1] = position
        self._timestamp_buffer[-1] = time.time()
        # set data
        self._scatter.setData(self._timestamp_buffer - time.time(), self._position_buffer)
        # x axis
        self.plot_widget.set_xlim(-10, 0)
        # y axis
        self._ymin = np.nanmin([np.nanmin(self._position_buffer), self._ymin])
        self._ymax = np.nanmax([np.nanmax(self._position_buffer), self._ymax])
        self.plot_widget.set_ylim(self._ymin, self._ymax)
        # labels
        self.plot_widget.set_labels(xlabel="seconds", ylabel="position")

    def _set_table(self):
        # busy
        self.busy = qtypes.Bool(disabled=True)
        self.table.append(self.busy, "busy")
        # id ---
        self.table.append(None, "id")
        # name
        name = qtypes.String(disabled=True)
        name.set(self.qclient.id()["name"])
        self.table.append(name, "name")
        # kind
        kind = qtypes.String(disabled=True)
        kind.set(self.qclient.id()["kind"])
        self.table.append(kind, "kind")
        # make
        make = qtypes.String(disabled=True)
        make.set(self.qclient.id()["make"])
        self.table.append(make, "make")
        # model
        model = qtypes.String(disabled=True)
        model.set(self.qclient.id()["model"])
        self.table.append(model, "model")
        # serial
        serial = qtypes.String(disabled=True)
        serial.set(self.qclient.id()["serial"])
        self.table.append(serial, "serial")
        # display
        self._set_table_display()

    def _set_table_display(self):
        self.table.append(None, "display")
        self.table.append(qtypes.Enum(), "scatter")
        text_keys = ["upper left", "upper right", "lower left", "lower right"]
        self._plot_text_enums = {k: qtypes.Enum() for k in text_keys}
        self._plot_text = {"upper left": self.plot_widget.add_text("upper left", anchor=(1,1)),
                                                                   }
        for key, enum in self._plot_text_enums.items():
            self.table.append(enum, key)
