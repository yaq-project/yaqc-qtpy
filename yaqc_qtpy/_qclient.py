__all__ = ["QClient"]


import types

import yaqc
from qtpy import QtCore

from ._dotdict import DotDict
from ._qproperty import QProperty
from ._qthread import QThreadedFunctionWrapper


class QClient(QtCore.QObject):
    reconnected = QtCore.Signal()
    busy_signal = QtCore.Signal(bool)
    poll_signal = QtCore.Signal()

    def __init__(self, host, port):
        super().__init__()
        self._client = yaqc.Client(host=host, port=port)
        self._client.register_connection_callback(self.reconnected.emit)
        self._id = self._client.id()
        self._cached_busy = None
        # messages
        for name, props in self._client._protocol.get("messages", {}).items():
            if hasattr(self, name):
                continue
            wrapped = QThreadedFunctionWrapper(getattr(self._client, name))
            setattr(self, name, wrapped)
        # properties
        self.properties = DotDict()
        for k, v in self._client._protocol.get("properties", {}).items():
            self.properties[k] = QProperty(self, v)
        self._poll_timer = QtCore.QTimer()
        self._poll_timer.start(500)
        self._poll_timer.timeout.connect(self._poll)
        # signals and slots
        self.busy.finished.connect(self._on_busy)

    @property
    def host(self):
        return self._client._host

    @property
    def port(self):
        return self._client._port

    def id(self):
        return self._id

    @property
    def traits(self):
        return self._client.traits

    def _on_busy(self, busy):
        # poll timer
        if busy:
            self._poll_timer.setInterval(100)
        else:
            self._poll_timer.setInterval(500)
        # signal
        if busy != self._cached_busy:
            self._cached_busy = busy
            self.busy_signal.emit(busy)

    def _poll(self):
        self.busy()
        for prop in self.properties.values():
            if prop.dynamic:
                prop()
                for k in ("units", "options", "limits"):
                    if hasattr(prop, k):
                        getattr(prop, k)()
        self.poll_signal.emit()
