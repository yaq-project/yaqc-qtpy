"""Class representing single property, see YEP-111."""


from qtpy import QtCore


Getter = object()
CachedResult = object()


class QProperty(QtCore.QObject):
    updated = QtCore.Signal(object)

    def __init__(self, qclient, prop):
        super().__init__()
        self._qclient = qclient
        self._property = prop
        self._getter = getattr(self._qclient, self._property["getter"])
        self._cached_result = CachedResult
        # attributes
        for k in ("units", "options", "limits"):
            if prop[f"{k}_getter"] is not None:
                setattr(self, k, getattr(self._qclient, self._property[f"{k}_getter"]))
        # signals and slots
        self._getter.finished.connect(self._on_getter)

    def __call__(self, val=Getter):
        if val is Getter:
            return self._getter()
        if not self._property["setter"]:
            raise TypeError("Property is not settable")
        return getattr(self._qclient, self._property["setter"])(val)

    def _on_getter(self, result):
        if result != self._cached_result:
            self.updated.emit(result)

    @property
    def control_kind(self):
        return self._property["control_kind"]

    @property
    def record_kind(self):
        return self._property["record_kind"]

    @property
    def dynamic(self):
        return self._property["dynamic"]

    @property
    def type(self):
        return self._property["type"]
