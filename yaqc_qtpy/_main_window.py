"""Main window."""


import sys
import functools

from qtpy import QtWidgets, QtCore
import qtypes

from ._main_widget import MainWidget
from ._qclient import QClient
from ._splash import Splash
from . import qtype_items


class MainWindow(QtWidgets.QMainWindow):
    shutdown = QtCore.Signal()
    queue_control = QtCore.Signal()

    def __init__(self, json):
        super().__init__(parent=None)
        self.setWindowTitle("yaqc-qtpy")
        # create widgets
        self._create_main_frame()
        self._main_widgets = {}
        self._qclients = {}

        for key, value in json.items():
            try:
                host, port = key.split(":")
                port = int(port)
                qclient = QClient(host=host, port=port)
                self._qclients[key] = qclient
                qtype_items.append_card_item(qclient, self._tree_widget)
                self._tree_widget[-1][-1].updated.connect(
                    functools.partial(self._show_main_widget, key=key)
                )
            except Exception:
                self._tree_widget.append(qtypes.String(value["name"], disabled=True))
                self._tree_widget[-1].set_value("offline")

        self._tree_widget.expandAll()
        self._tree_widget.resizeColumnToContents(0)

        self.setStyleSheet("".join(qtypes.styles["tomorrow-night"].values()))

    def _create_main_frame(self):
        splitter = QtWidgets.QSplitter()
        # left hand tree
        self._tree_widget = qtypes.TreeWidget(width=500)
        splitter.addWidget(self._tree_widget)
        # expanding area
        self._main_widget_container = QtWidgets.QWidget()
        self._main_widget_container.setLayout(QtWidgets.QHBoxLayout())
        self._main_widget_container.layout().setContentsMargins(0, 0, 0, 0)
        self._splash = Splash()
        self._main_widget_container.layout().addWidget(self._splash)
        splitter.addWidget(self._main_widget_container)
        # finish
        self.setCentralWidget(splitter)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 50)

    def _show_main_widget(self, key):
        self._splash.hide()
        for widget in self._main_widgets.values():
            widget.hide()
        if key not in self._main_widgets:
            self._main_widgets[key] = MainWidget(qclient=self._qclients[key], parent=self)
            self._main_widget_container.layout().addWidget(self._main_widgets[key])
        self._main_widgets[key].show()
        # self._view_buttons[key].setText("VIEWING ADVANCED")
        # self._view_buttons[key].set_background("yellow")
