"""Main window."""


import sys
import functools
import pathlib

import appdirs
from qtpy import QtWidgets, QtCore
import qtypes

from ._main_widget import MainWidget
from ._qclient import QClient
from ._splash import Splash
from ._lru_dict import LRUDict
from . import qtype_items


def calc_position(item, name):
    out = 0
    if not item.children:
        return 0
    while name > item.children[out].get()["label"]:
        if isinstance(item[out], qtypes.Null):
            break
        out += 1
        if out >= len(item.children):
            break
    return out


class MainWindow(QtWidgets.QMainWindow):
    shutdown = QtCore.Signal()
    queue_control = QtCore.Signal()

    def __init__(self, json):
        super().__init__(parent=None)
        self.setWindowTitle("yaqc-qtpy")
        # create widgets
        self._create_main_frame()
        self._main_widgets = LRUDict(maxsize=3, cleanup=lambda x: x.close())
        self._qclients = {}
        config = pathlib.Path(appdirs.user_config_dir("yaqc-qtpy", "yaq"))
        config.mkdir(exist_ok=True, parents=True)
        self.hidden_path = config / "hidden.txt"
        self.hidden_path.touch()
        with open(self.hidden_path, "r") as conf:
            self.hidden = {x.strip() for x in conf.readlines()}
        self._hidden = qtypes.Null("hidden")
        self._root_item.append(self._hidden)

        with self._root_item.suppress_restructured():
            for key, value in json.items():
                self._add_card(key, value["name"])

        for i in range(len(self._tree_widget) - 1):
            self._tree_widget[i].expand(0)
        self._tree_widget.resizeColumnToContents(0)
        self.setStyleSheet("".join(qtypes.styles["tomorrow-night"].values()))

    def _create_main_frame(self):
        splitter = QtWidgets.QSplitter()
        # left hand tree
        self._root_item = qtypes.Null()
        self._tree_widget = qtypes.TreeWidget(self._root_item)
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

    def _toggle_hide(self, key, label):
        self.hidden.symmetric_difference_update({key})
        with open(self.hidden_path, "wt") as f:
            for i in self.hidden:
                f.write(i + "\n")
        self._remove_card(label)
        self._add_card(key, label)
        for i in range(len(self._tree_widget) - 1):
            self._tree_widget[i].expand(0)

    def _remove_card(self, key):
        if key in self._hidden:
            self._hidden.pop(key)
        elif key in self._root_item:
            self._root_item.pop(key)

    def _add_card(self, key, name):
        tree = self._root_item
        if key in self.hidden:
            tree = self._hidden
        try:
            host, port = key.split(":")
            port = int(port)
            qclient = QClient(host=host, port=port)
            self._qclients[key] = qclient
            pos = calc_position(tree, qclient.id()["name"])
            card = qtype_items.append_card_item(qclient, tree, pos)
            view_advanced = tree[pos][-1]
            if view_advanced.get()["label"] != "":
                view_advanced = tree[pos][-2]
            view_advanced.updated_connect(
                lambda _: functools.partial(self._show_main_widget, key=key)()
            )
            view_advanced.append(
                qtypes.Button("", text="Unhide" if tree == self._hidden else "Hide")
            )
            view_advanced[-1].updated_connect(
                lambda _: functools.partial(
                    self._toggle_hide, key=key, label=card.get()["label"]
                )()
            )

        except Exception as e:
            card = qtypes.String(name, disabled=True)
            pos = calc_position(tree, name)
            tree.insert(pos, card)
            tree[pos].set_value("offline")
            tree[pos].append(qtypes.Button("", text="Unhide" if tree == self._hidden else "Hide"))
            tree[pos][-1].updated_connect(
                functools.partial(self._toggle_hide, key=key, label=card.get()["label"])
            )
