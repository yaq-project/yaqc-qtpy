from qtpy import QtWidgets, QtCore



class ConfigWidget(QtWidgets.QPlainTextEdit):

    def __init__(self, qclient, parent):
        super().__init__(parent=parent)
        self.qclient = qclient
        self.qclient.get_config.finished.connect(self.on_get_config)
        self.qclient.get_config()

    def on_get_config(self, result):
        self.setPlainText(result)
