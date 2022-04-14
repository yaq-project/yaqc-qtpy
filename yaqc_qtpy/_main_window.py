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
    while name > item.children[out].text(0):
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
        self._hidden = qtypes.Null("Hidden")
        self._tree_widget.append(self._hidden)

        for key, value in json.items():
            self._add_card(key, value["name"])
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

    def _toggle_hide(self, key):
        self.hidden.symmetric_difference_update({key})
        with open(self.hidden_path, "wt") as f:
            for i in self.hidden:
                f.write(i + "\n")
        name = self._remove_card(key)
        self._add_card(key, name)

    def _remove_card(self, key):
        ret = key
        for index, card in enumerate(self._tree_widget.children):
            if isinstance(card, qtypes.Null):
                continue
            if card.key == key:
                card.setHidden(True)
                ret = card.text(0)
        for index, card in enumerate(self._hidden.children):
            if card.key == key:
                card.setHidden(True)
                ret = card.text(0)
        return ret

    def _add_card(self, key, name):
        tree = self._tree_widget
        if key in self.hidden:
            tree = self._hidden
        try:
            host, port = key.split(":")
            port = int(port)
            qclient = QClient(host=host, port=port)
            self._qclients[key] = qclient
            pos = calc_position(tree, qclient.id()["name"])
            card = qtype_items.append_card_item(qclient, tree, pos)
            setattr(card, "key", key)
            card.setExpanded(True)
            view_advanced = tree[pos][-1]
            if view_advanced.text(0) != "":
                view_advanced = tree[pos][-2]
            view_advanced.updated.connect(functools.partial(self._show_main_widget, key=key))
            view_advanced.append(
                qtypes.Button("", value={"text": "Unhide" if tree == self._hidden else "Hide"})
            )
            view_advanced[-1].updated.connect(functools.partial(self._toggle_hide, key=key))

        except Exception as e:
            print(e)
            card = qtypes.String(name, disabled=True)
            setattr(card, "key", key)
            pos = calc_position(tree, name)
            tree.insert(pos, card)
            tree[pos].set_value("offline")
            tree[pos].append(
                qtypes.Button("", value={"text": "Unhide" if tree == self._hidden else "Hide"})
            )
            tree[pos][-1].updated.connect(functools.partial(self._toggle_hide, key=key))
