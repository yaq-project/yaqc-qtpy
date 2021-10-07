__all__ = ["QClient"]


from qtpy import QtCore


class QProperty(QtCore.QObject):
    updated: QtCore.Signal
    set: QtCore.Signal




class QClient(QtCore.QObject):
    pass
