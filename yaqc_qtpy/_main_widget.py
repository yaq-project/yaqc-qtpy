from qtpy import QtWidgets, QtCore
import qtypes
import yaqc
import numpy as np
import entrypoints

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.manager import QtKernelManager

from ._config_widget import ConfigWidget
from ._has_position_widget import HasPositionWidget
from ._is_sensor_widget import IsSensorWidget
from ._plot import Plot1D

# The ID of an installed kernel, e.g. 'bash' or 'ir'.
USE_KERNEL = 'python3'

# This function was copied from the qtconsole embedding example code
# https://github.com/jupyter/qtconsole/blob/b4e08f763ef1334d3560d8dac1d7f9095859545a/examples/embed_qtconsole.py#L19
def make_jupyter_widget_with_kernel():
    """Start a kernel, connect to it, and create a RichJupyterWidget to use it
    """
    kernel_manager = QtKernelManager(kernel_name=USE_KERNEL)
    kernel_manager.start_kernel()

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()

    jupyter_widget = RichJupyterWidget()
    jupyter_widget.set_default_style("linux")  # Dark bg color.... only key to get it...
    jupyter_widget.kernel_manager = kernel_manager
    jupyter_widget.kernel_client = kernel_client
    return jupyter_widget

class MainWidget(QtWidgets.QTabWidget):
    def __init__(self, qclient, *, parent=None):
        super().__init__(parent=parent)
        self.qclient = qclient
        self.addTab(ConfigWidget(qclient=self.qclient, parent=self), "config")
        ipy = make_jupyter_widget_with_kernel()
        ipy.execute(f"""import yaqc
c = yaqc.Client(host='{self.qclient.host}', port={self.qclient.port})
{self.qclient.id()["name"]} = c
""")
        print(dir(ipy))
        self.addTab(ipy, "console")
        if "has-position" in self.qclient.traits:
            self.addTab(HasPositionWidget(qclient=self.qclient, parent=self), "has-position")
        if "is-sensor" in self.qclient.traits:
            self.addTab(IsSensorWidget(qclient=self.qclient, parent=self), "is-sensor")
        # gui tabs provided via entrypoints
        group_name = self.qclient._client._protocol['protocol'].replace("-", "_")
        group = f"yaqc_qtpy.main.{group_name}"
        for ep in entrypoints.get_group_all(group):
            print(ep)
            self.addTab(ep.load()(qclient), ep.name)
        self.setCurrentIndex(self.count() - 1)

    def poll(self):
        pass
