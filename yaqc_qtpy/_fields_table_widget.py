from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import json

from ._plot import Plot1D


class FieldsTableWidget(qtypes.widgets.InputTable):

    def __init__(self, host: str, port: int, verbose=False):
        super().__init__()
        self.host = host
        self.port = port
        try:
            self.client = yaqc.Client(host=host, port=port)
        except Exception as e:
            print(e)
        if len(self.client._protocol.get("fields", {})) > 0:
            fields = self.client._protocol["fields"]
            for k, d in fields.items():
                if type(d) == str:  # somehow we get traits here sometimes...
                    continue
                if d["fields"]["kind"] == "normal" and not verbose:
                    continue
                self._append_trait(k, **d["fields"])

    def _append_trait(self, key, **kwargs):
        print(key, kwargs)
        if "setter" in kwargs.keys():
            disabled = False
        else:
            disabled = True
        if kwargs["type"] == "boolean":
            pass   # TODO:
        elif kwargs["type"] in ["double"]:
            number = qtypes.Number(disabled=disabled, name=key)
            self.append(number, key)
            number.updated.connect(lambda: self._set_trait(key, kwargs, number))
        elif kwargs["type"] == "string" and "options_getter" in kwargs.keys():
            allowed_values = getattr(self.client, kwargs["options_getter"])()
            enum = qtypes.Enum(disabled=disabled, allowed_values=allowed_values, name=key)
            self.append(enum, key)
        elif kwargs["type"] == "string":
            string = qtypes.String(disabled=disabled, name=key)
            self.append(string, key)
        else:
            pass

    def poll(self):
        if len(self.client._protocol.get("fields", {})) > 0:
            fields = self.client._protocol["fields"]
        else:
            return
        for k, d in fields.items():
            print(k, d)
            if k in self._objs.keys():
                getter = getattr(self.client, d["fields"]["getter"])
                new = getter()
                print(new)
                self[k].set(new)

    def _set_trait(self, key, kwargs, qtypes_object):
        setter = getattr(self.client, kwargs["setter"])
        setter(qtypes_object.get())
