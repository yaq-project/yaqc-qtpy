"""Main window."""


import sys

from qtpy import QtWidgets, QtCore
import qtypes

from ._card_widget import CardWidget
from ._main_widget import MainWidget
from ._qclient import QClient
from ._splash import Splash


class MainWindow(QtWidgets.QMainWindow):
    shutdown = QtCore.Signal()
    queue_control = QtCore.Signal()

    def __init__(self, json):
        super().__init__(parent=None)
        self.setWindowTitle("yaqc-qtpy")
        # create widgets
        self._create_main_frame()
        self._card_widgets = {}
        self._view_buttons = {}
        self._main_widgets = {}
        self._qclients = {}
        for key, value in json.items():
            host, port = key.split(":")
            port = int(port)
            self._qclients[key] = QClient(host=host, port=port)
            self._create_card(key)

    def _create_card(self, key):
        # card widget
        cw =  CardWidget(qclient=self._qclients[key])
        self._card_widgets[key] = cw
        self.scroll_area.add_widget(cw)
        # button
        if cw.qclient is not None:
            button = qtypes.widgets.PushButton(label="VIEW ADVANCED", background="green")
        else:
            button = qtypes.widgets.PushButton(label="OFFLINE", background="red")
        button.clicked.connect(lambda: self._show_main_widget(key))
        self.scroll_area.add_widget(button)
        self._view_buttons[key] = button

    def _create_main_frame(self):
        self.main_frame = QtWidgets.QWidget(parent=self)
        hbox = QtWidgets.QHBoxLayout()
        # left hand scroll area
        self.scroll_area = qtypes.widgets.ScrollArea()
        hbox.addWidget(self.scroll_area)
        # expanding area
        self._big_box = QtWidgets.QVBoxLayout()
        self._splash = Splash()
        self._big_box.addWidget(self._splash)
        hbox.addLayout(self._big_box)
        # finish
        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)

    def _show_main_widget(self, key):
        self._splash.hide()
        for button in self._view_buttons.values():
            button.setText("VIEW ADVANCED")
            button.set_background("green")
        for widget in self._main_widgets.values():
            widget.hide()
        if key not in self._main_widgets:
            self._main_widgets[key] = MainWidget(qclient=self._qclients[key], parent=self)
            self._big_box.addWidget(self._main_widgets[key])
        self._main_widgets[key].show()
        self._view_buttons[key].setText("VIEWING ADVANCED")
        self._view_buttons[key].set_background("yellow")
