from collections import deque
import time
import warnings

from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np
import yaq_traits

from ._plot import Plot1D, BigNumberWidget
from . import qtype_items


class IsSensorWidget(QtWidgets.QSplitter):
    def __init__(self, qclient, *, parent=None):
        super().__init__(parent=parent)
        self.qclient = qclient
        self.get_channel_metadata()  # blocks until complete
        self._create_main_frame()
        # plotting variables
        self._position_buffer = deque(maxlen=250)
        self._timestamp_buffer = deque(maxlen=250)
        # signals and slots
        self.qclient.get_measured.finished.connect(self._on_get_measured)
        self.qclient.get_measurement_id.finished.connect(self._on_get_measurement_id)
        self._poll_timer = QtCore.QTimer()
        self._poll_timer.start(500)
        self._poll_timer.timeout.connect(self._poll)
        self._poll_period.updated.connect(self._on_poll_period_updated)
        self._last_plotted_measurement_id = float("nan")

    def _create_main_frame(self):
        # plot
        plot_container_widget = QtWidgets.QWidget()
        plot_container_widget.setLayout(QtWidgets.QVBoxLayout())
        plot_container_widget.layout().setContentsMargins(0, 0, 0, 0)
        self._big_number = BigNumberWidget()
        plot_container_widget.layout().addWidget(self._big_number)
        self.plot_widget = Plot1D()
        self._destination_line = self.plot_widget.add_infinite_line(
            hide=False, angle=0, color="#b5bd68"
        )
        self._scatter = self.plot_widget.add_scatter()
        plot_container_widget.layout().addWidget(self.plot_widget)
        self.addWidget(plot_container_widget)

        # right hand tree
        self._tree_widget = qtypes.TreeWidget(width=500)

        # plot control
        plot_item = qtypes.Null("plot")
        self._tree_widget.append(plot_item)
        x_item = qtypes.Null("x axis")
        plot_item.append(x_item)
        self._cached_count = qtypes.Integer(
            "cached values", value={"value": 250, "minimum": 0, "maximum": 1000}
        )
        self._cached_count.updated.connect(self._on_cached_count_updated)
        x_item.append(self._cached_count)
        self._poll_period = qtypes.Float(
            "poll period (s)", value={"value": 0.5, "minimum": 0, "maximum": 1000}
        )
        x_item.append(self._poll_period)
        self._xmin = qtypes.Float("xmin (s)", value={"value": -60, "minimum": -100, "maximum": 0})
        self._xmin.updated.connect(self._on_xmin_updated)
        x_item.append(self._xmin)
        x_item.setExpanded(True)
        y_item = qtypes.Null("y axis")
        plot_item.append(y_item)
        self._channel_selector = qtypes.Enum(
            "channel", value={"allowed": list(self._channel_shapes.keys())}
        )
        self._channel_selector.updated.connect(self._on_channel_selector_updated)
        y_item.append(self._channel_selector)
        self._lock_ylim = qtypes.Bool("lock ylim", value={"value": False})
        self._lock_ylim.updated.connect(self._on_lock_ylim)
        y_item.append(self._lock_ylim)
        self._ymax = qtypes.Float("ymax", disabled=True)
        y_item.append(self._ymax)
        self._ymin = qtypes.Float("ymin", disabled=True)
        y_item.append(self._ymin)
        self._reset_ylim = qtypes.Button("reset ylim", value={"text": "reset"})
        self._reset_ylim.updated.connect(self._on_reset_ylim)
        y_item.append(self._reset_ylim)
        y_item.setExpanded(True)
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

        self._tree_widget.resizeColumnToContents(0)
        self.addWidget(self._tree_widget)

    def get_channel_metadata(self):
        shapes_task = self.qclient.get_channel_shapes()
        units_task = self.qclient.get_channel_units()
        while not shapes_task.finished:
            time.sleep(0.01)
        while not units_task.finished:
            time.sleep(0.01)
        self._channel_shapes = shapes_task.result
        self._channel_units = shapes_task.result

    def _on_get_measurement_id(self, measurement_id):
        self._scatter.setData(
            np.array(self._timestamp_buffer) - time.time(), self._position_buffer
        )
        if self._last_plotted_measurement_id != measurement_id:
            self.qclient.get_measured()

    def _on_get_measured(self, measured):
        self._last_plotted_measurement_id = measured["measurement_id"]
        measured = measured[self._channel_selector.get_value()]
        self._big_number.set_label(self._channel_selector.get_value())
        self._big_number.set_number(measured)
        # enter new data
        self._position_buffer.append(measured)
        self._timestamp_buffer.append(time.time())
        # set data
        self._scatter.setData(
            np.array(self._timestamp_buffer) - time.time(), self._position_buffer
        )
        # x axis
        self.plot_widget.set_xlim(self._xmin.get_value(), 0)
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

    def _on_lock_ylim(self, dic):
        locked = dic["value"]
        self._ymin.disabled.emit(not locked)
        self._ymax.disabled.emit(not locked)

    def _on_poll_period_updated(self, dic):
        self._poll_timer.setInterval(int(dic["value"] * 1000))

    def _poll(self):
        self.qclient.get_measurement_id()

    def _on_channel_selector_updated(self, _=None):
        self._position_buffer = deque(maxlen=self._cached_count.get_value())
        self._timestamp_buffer = deque(maxlen=self._cached_count.get_value())

    def _on_cached_count_updated(self, value):
        position_buffer = deque(maxlen=value["value"])
        timestamp_buffer = deque(maxlen=value["value"])

        for p, t in zip(self._position_buffer, self._timestamp_buffer):
            position_buffer.append(p)
            timestamp_buffer.append(t)

        self._position_buffer = position_buffer
        self._timestamp_buffer = timestamp_buffer

    def _on_xmin_updated(self, value):
        self.plot_widget.set_xlim(value["value"], 0)

    def _on_reset_ylim(self, _=None):
        self._ymin.set_value(np.nanmin(self._position_buffer))
        self._ymax.set_value(np.nanmax(self._position_buffer))

    def close(self):
        super().close()
        self.qclient.get_measured.finished.disconnect(self._on_get_measured)
