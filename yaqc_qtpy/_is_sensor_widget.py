from collections import deque
import time
import warnings

from qtpy import QtWidgets, QtCore
import qtypes
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
        self._measure_1d = np.array([0])
        self._ndim = 0
        self._timestamp_buffer = deque(maxlen=250)
        # signals and slots
        self.qclient.get_measured.finished.connect(self._on_get_measured)
        self.qclient.get_measurement_id.finished.connect(self._on_get_measurement_id)
        self._poll_timer = QtCore.QTimer()
        self._poll_timer.start(500)
        self._poll_timer.timeout.connect(self._poll)
        self._poll_period.updated_connect(self._on_poll_period_updated)
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
        self._image = self.plot_widget.add_image()
        plot_container_widget.layout().addWidget(self.plot_widget)
        self.addWidget(plot_container_widget)

        # right hand tree
        self._root_item = qtypes.Null()

        # plot control
        plot_item = qtypes.Null("plot")
        self._root_item.append(plot_item)
        self._channel_selector = qtypes.Enum("channel", allowed=list(self._channel_shapes.keys()))
        self._channel_selector.updated_connect(self._on_channel_selector_updated)
        plot_item.append(self._channel_selector)
        self._poll_period = qtypes.Float("poll period (s)", value=0.5, minimum=0, maximum=1000)
        plot_item.append(self._poll_period)

        scalar_item = qtypes.Null("Scalar channel")
        plot_item.append(scalar_item)
        self._cached_count = qtypes.Integer("cached values", value=250, minimum=0, maximum=1000)
        self._cached_count.updated_connect(self._on_cached_count_updated)
        scalar_item.append(self._cached_count)
        self._xmin = qtypes.Float("xmin (s)", value=-60, minimum=-100, maximum=0)
        self._xmin.updated_connect(self._on_xmin_updated)
        scalar_item.append(self._xmin)
        self._lock_ylim = qtypes.Bool("lock ylim", value=False)
        self._lock_ylim.updated_connect(self._on_lock_ylim)
        scalar_item.append(self._lock_ylim)
        self._ymax = qtypes.Float("ymax", disabled=True)
        scalar_item.append(self._ymax)
        self._ymin = qtypes.Float("ymin", disabled=True)
        scalar_item.append(self._ymin)
        self._reset_ylim = qtypes.Button("reset ylim", text="reset")
        self._reset_ylim.updated_connect(self._on_reset_ylim)
        scalar_item.append(self._reset_ylim)

        one_d_plot_item = qtypes.Null("1D channel")
        plot_item.append(one_d_plot_item)
        self._1d_mapping = qtypes.Enum("mapping", allowed=["none"])
        self._lock_ylim_1d = qtypes.Bool("lock ylim", value=False)
        self._lock_ylim_1d.updated_connect(self._on_lock_ylim)
        one_d_plot_item.append(self._lock_ylim_1d)
        self._ymax_1d = qtypes.Float("ymax", disabled=True)
        one_d_plot_item.append(self._ymax)
        self._ymin_1d = qtypes.Float("ymin", disabled=True)
        one_d_plot_item.append(self._ymin)
        self._reset_ylim_1d = qtypes.Button("reset ylim", text="reset")
        self._reset_ylim_1d.updated_connect(self._on_reset_ylim_1d)
        one_d_plot_item.append(self._reset_ylim_1d)

        image_item = qtypes.Null("Image channel")
        plot_item.append(image_item)
        self._image_origin = qtypes.Enum("image origin", allowed=["upper", "lower"])
        self._image_origin.updated_connect(lambda _: self.qclient.get_measured())
        image_item.append(self._image_origin)
        self._lock_zlim = qtypes.Bool("lock zlim", value=False)
        self._lock_zlim.updated_connect(self._on_lock_zlim)
        image_item.append(self._lock_zlim)
        self._zmax = qtypes.Float("zmax", disabled=True)
        image_item.append(self._zmax)
        self._zmin = qtypes.Float("zmin", disabled=True)
        image_item.append(self._zmin)
        self._lock_aspect = qtypes.Bool("lock aspect", value=True)
        image_item.append(self._lock_aspect)
        self._lock_aspect.updated_connect(self._on_lock_aspect)
        self._aspect = qtypes.Float("aspect", value=1)
        image_item.append(self._aspect)

        # id
        id_item = qtypes.Null("id")
        self._root_item.append(id_item)
        for key, value in self.qclient.id().items():
            id_item.append(qtypes.String(label=key, disabled=True, value=value))
            if key == "name":
                self._big_number.set_label(value)

        # traits
        traits_item = qtypes.Null("traits")
        self._root_item.append(traits_item)
        for trait in yaq_traits.__traits__.traits.keys():
            traits_item.append(
                qtypes.Bool(label=trait, disabled=True, value=trait in self.qclient.traits)
            )

        # properties
        properties_item = qtypes.Null("properties")
        self._root_item.append(properties_item)
        qtype_items.append_properties(self.qclient, properties_item)

        self._tree_widget = qtypes.TreeWidget(self._root_item)
        self._tree_widget["plot"].expand()
        self._tree_widget["id"].expand()
        self._tree_widget["properties"].expand()
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
        if self._ndim == 0:
            self._scatter.setData(
                np.array(self._timestamp_buffer) - time.time(), self._position_buffer
            )
        if self._last_plotted_measurement_id != measurement_id:
            self.qclient.get_measured()

    def _on_get_measured(self, measured):
        self._last_plotted_measurement_id = measured["measurement_id"]
        measured = measured[self._channel_selector.get_value()]
        ndim = np.ndim(measured)
        self._ndim = ndim

        self._big_number.set_label(self._channel_selector.get_value())

        if ndim == 0:
            self._big_number.set_number(measured)
            self._destination_line.setPen("#b5bd68")
            # enter new data
            self._position_buffer.append(measured)
            self._timestamp_buffer.append(time.time())
            self.plot_widget.plot_object.setAspectLocked(False)
            # set data
            self._image.setImage(np.array([[0]]))
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
        elif ndim == 1:
            self._measure_1d = measured
            self._big_number.set_number(measured.max())
            self._destination_line.setPen("#b5bd68")
            # enter new data
            self.plot_widget.plot_object.setAspectLocked(False)
            # set data
            self._scatter.setData(np.arange(len(measured)), measured)
            self.plot_widget.set_xlim(0, len(measured))
            self._image.setImage(np.array([[0]]))
            # y axis
            if not self._lock_ylim_1d.get_value():
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    ymin = self._ymin_1d.get_value()
                    ymax = self._ymax_1d.get_value()
                    ymin = np.nanmin([np.nanmin(measured), ymin])
                    ymax = np.nanmax([np.nanmax(measured), ymax])
                if ymin == ymax:
                    ymin -= 1e-6
                    ymax += 1e-6
                self._ymin.set_value(ymin)
                self._ymax.set_value(ymax)
            self.plot_widget.set_ylim(self._ymin.get_value(), self._ymax.get_value())
            # labels
            self.plot_widget.set_labels(xlabel="index", ylabel="")
        elif ndim == 2 or ndim == 3:
            if self._image_origin.get_value() == "upper":
                measured = measured[::-1, :]
            self._big_number.set_number(measured.max())
            if self._lock_aspect.get_value():
                self.plot_widget.plot_object.setAspectLocked(True, self._aspect.get_value())
            else:
                self.plot_widget.plot_object.setAspectLocked(False)

            self._destination_line.setPen("#0000")
            self._scatter.setData([], [])
            self._image.setImage(measured.T, autoLevels=not self._lock_zlim.get_value())
            if self._lock_zlim.get_value():
                self._image.setLevels([self._zmin.get_value(), self._zmax.get_value()])
            else:
                zmin, zmax = self._image.getLevels()
                self._zmin.set_value(zmin)
                self._zmax.set_value(zmax)
            self.plot_widget.set_ylim(0, len(measured))
            self.plot_widget.set_xlim(0, len(measured.T))
            self.plot_widget.set_labels(xlabel="", ylabel="")

    def _on_lock_ylim(self, dic):
        locked = dic["value"]
        self._ymin.set({"disabled": not locked})
        self._ymax.set({"disabled": not locked})

    def _on_lock_ylim_1d(self, dic):
        locked = dic["value"]
        self._ymin_1d.set({"disabled": not locked})
        self._ymax_1d.set({"disabled": not locked})

    def _on_lock_zlim(self, dic):
        locked = dic["value"]
        self._zmin.set({"disabled": not locked})
        self._zmax.set({"disabled": not locked})

    def _on_lock_aspect(self, dic):
        locked = dic["value"]
        self._aspect.set({"disabled": not locked})

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

    def _on_reset_ylim_1d(self, _=None):
        self._ymin_1d.set_value(np.nanmin(self._measure_1d))
        self._ymax_1d.set_value(np.nanmax(self._measure_1d))

    def close(self):
        super().close()
        self.qclient.get_measured.finished.disconnect(self._on_get_measured)
