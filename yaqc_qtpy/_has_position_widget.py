import time
import warnings
from functools import partial

from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np
import yaq_traits

from ._plot import Plot1D
from . import qtype_items


class HasPositionWidget(QtWidgets.QSplitter):
    def __init__(self, qclient, *, parent=None):
        super().__init__(parent=parent)
        self.qclient = qclient
        self._create_main_frame()
        # plotting variables
        self._position_buffer = np.full(100, np.nan)
        self._timestamp_buffer = np.full(100, np.nan)
        self._ymin = -1e-6
        self._ymax = 1e-6
        # signals and slots
        if "position" in self.qclient.properties:
            self.qclient.properties.position.updated.connect(self._on_position_updated)

    def _create_main_frame(self):
        # plot
        self.plot_widget = Plot1D()
        self._scatter = self.plot_widget.add_scatter()
        self.addWidget(self.plot_widget)
        # right hand tree
        self._tree_widget = qtypes.TreeWidget(width=500)

        # id
        id_item = qtypes.Null("id")
        self._tree_widget.append(id_item)
        for key, value in self.qclient.id().items():
            id_item.append(qtypes.String(label=key, disabled=True, value={"value": value}))
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._ymin = np.nanmin([np.nanmin(self._position_buffer), self._ymin])
            self._ymax = np.nanmax([np.nanmax(self._position_buffer), self._ymax])
        self.plot_widget.set_ylim(self._ymin, self._ymax)
        # labels
        self.plot_widget.set_labels(xlabel="seconds", ylabel="position")
