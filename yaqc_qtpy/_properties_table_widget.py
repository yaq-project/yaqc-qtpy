from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import json
import numpy as np
import functools

from ._plot import Plot1D


class PropertiesTableWidget(qtypes.widgets.InputTable):

    def __init__(self, qclient, verbose=False, *, parent=None):
        super().__init__()
        self.qclient = qclient
        if verbose:
            self.append(None, "properties")
        for key, property in self.qclient.properties.items():
            self._append_property(key, property)

    def _append_property(self, key, property):
        # disabled
        if property._property.get("setter", None):
            disabled = False
        else:
            disabled = True
        # widgets
        if property.type == "boolean":
            pass   # TODO:
        elif property.type in ["double"]:
            number = qtypes.Number(disabled=disabled, name=key)
            self.append(number, key)
            if not disabled:
                number.edited.connect(lambda: self._set_property(key, number))
        elif property.type == "string" and "options_getter" in property._property.keys():
            return
            allowed_values = getattr(self.client, property._property["options_getter"])()
            enum = qtypes.Enum(disabled=disabled, allowed_values=allowed_values, name=key)
            self.append(enum, key)
            if not disabled:
                enum.edited.connect(lambda: self._set_trait(key, enum))
        elif property.type == "string":
            string = qtypes.String(disabled=disabled, name=key)
            self.append(string, key)
        else:
            pass
        # updated signal
        property.updated.connect(functools.partial(self._on_property_updated, key=key))

    def _on_property_updated(self, value, *, key=None):
        self._objs[key].set(value)

    def _set_property(self, key, qtypes_object):
        property = self.qclient.properties[key]
        property.__call__(qtypes_object.get())
