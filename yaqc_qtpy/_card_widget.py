from qtpy import QtWidgets, QtCore
import qtypes
from qtypes._base import Base
import yaqc



class CardItem(Base):

    def __init__(self, qclient):
        super().__init__()
        self.qclient = qclient
        self.append(qtypes.Bool(label=f"{qclient.host}:{qclient.port}"))
