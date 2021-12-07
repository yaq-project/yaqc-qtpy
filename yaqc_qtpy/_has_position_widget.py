import time
import warnings
from functools import partial

from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np
import yaq_traits

from ._plot import Plot1D, BigNumberWidget
from . import qtype_items


class HasPositionWidget(QtWidgets.QSplitter):
    def __init__(self, qclient, *, parent=None):
        super().__init__(parent=parent)
        self.qclient = qclient
        self._create_main_frame()
        # plotting variables
        self._position_buffer = np.full(250, np.nan)
        self._timestamp_buffer = np.full(250, np.nan)
        # signals and slots
        if "position" in self.qclient.properties:
            self.qclient.properties.position.updated.connect(self._on_position_updated)
            self.qclient.properties.destination.updated.connect(self._on_destination_updated)
        if "has-limits" in self.qclient.traits:
            self.qclient.get_limits.finished.connect(self._on_get_limits)
            self.qclient.get_limits()

    def _create_main_frame(self):
        # plot
        plot_container_widget = QtWidgets.QWidget()
        plot_container_widget.setLayout(QtWidgets.QVBoxLayout())
        plot_container_widget.layout().setContentsMargins(0,0,0,0)
        self._big_number = BigNumberWidget()
        plot_container_widget.layout().addWidget(self._big_number)
        self.plot_widget = Plot1D()
        self._minimum_line = self.plot_widget.add_infinite_line(hide=False, angle=0, color="#cc6666")
        self._maximum_line = self.plot_widget.add_infinite_line(hide=False, angle=0, color="#cc6666")
        self._destination_line = self.plot_widget.add_infinite_line(hide=False, angle=0, color="#b5bd68")
        self._scatter = self.plot_widget.add_scatter()
        plot_container_widget.layout().addWidget(self.plot_widget)
        self.addWidget(plot_container_widget)

        # right hand tree
        self._tree_widget = qtypes.TreeWidget(width=500)

        # plot control
        plot_item = qtypes.Null("plot")
        self._tree_widget.append(plot_item)
        self._lock_ylim = qtypes.Bool("lock ylim", value={"value":False})
        self._lock_ylim.updated.connect(self._on_lock_ylim)
        plot_item.append(self._lock_ylim)
        self._ymax = qtypes.Float("ymax", disabled=True)
        plot_item.append(self._ymax)
        self._ymin = qtypes.Float("ymin", disabled=True)
        plot_item.append(self._ymin)
        plot_item.setExpanded(True)

        # id
        id_item = qtypes.Null("id")
        self._tree_widget.append(id_item)
        for key, value in self.qclient.id().items():
            id_item.append(qtypes.String(label=key, disabled=True, value={"value": value}))
            if key == "name":
                self._big_number.set_label(value)
        id_item.setExpanded(True)

        # traits
        traits_item = qtypes.Null("traits")
        self._tree_widget.append(traits_item)
        for trait in yaq_traits.__traits__.traits.keys():
            traits_item.append(
                qtypes.Bool(
                    label=trait, disabled=True, value={"value": trait in self.qclient.traits}
                )
            )

        # properties
        properties_item = qtypes.Null("properties")
        self._tree_widget.append(properties_item)
        qtype_items.append_properties(self.qclient, properties_item)
        properties_item.setExpanded(True)

        # is-homeable
        if "is-homeable" in self.qclient.traits:

            def on_clicked(_, qclient):
                qclient.home()

            home_button = qtypes.Button("is-homeable", value={"text": "home"})
            self._tree_widget.append(home_button)
            home_button.updated.connect(partial(on_clicked, qclient=self.qclient))

        self._tree_widget.resizeColumnToContents(0)
        self.addWidget(self._tree_widget)

    def _on_destination_updated(self, destination):
        self._destination_line.setValue(destination)

    def _on_get_limits(self, result):
        self._minimum_line.setValue(min(result))
        self._maximum_line.setValue(max(result))

    def _on_lock_ylim(self, dic):
        locked = dic["value"]
        self._ymin.disabled.emit(not locked)
        self._ymax.disabled.emit(not locked)

    def _on_position_updated(self, position):
        self._big_number.set_number(position)
        # roll over, enter new data
        self._position_buffer = np.roll(self._position_buffer, -1)
        self._timestamp_buffer = np.roll(self._timestamp_buffer, -1)
        self._position_buffer[-1] = position
        self._timestamp_buffer[-1] = time.time()
        # set data
        self._scatter.setData(self._timestamp_buffer - time.time(), self._position_buffer)
        # x axis
        self.plot_widget.set_xlim(-60, 0)
        # y axis
        if not self._lock_ylim.get_value():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ymin = self._ymin.get_value()
                ymax = self._ymax.get_value()
                ymin = np.nanmin([np.nanmin(self._position_buffer), ymin])
                ymax = np.nanmax([np.nanmax(self._position_buffer), ymax])
            if ymin == ymax:
                ymin -= 1e-6
                ymax += 1e-6
            self._ymin.set_value(ymin)
            self._ymax.set_value(ymax)
        self.plot_widget.set_ylim(self._ymin.get_value(), self._ymax.get_value())
        # labels
        self.plot_widget.set_labels(xlabel="seconds", ylabel="position")
