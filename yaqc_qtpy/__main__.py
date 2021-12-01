import sys

import click
import json
from qtpy import QtWidgets
import yaqd_control

from ._main_window import MainWindow
from .__version__ import __version__


@click.command()
@click.argument("input", type=click.File("rb"), default=None, required=False)
def main(input):
    if input is None:
        input = json.loads(yaqd_control.list_(format="json"))
    else:
        input = json.load(input)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(input)
    window.show()
    window.showMaximized()
    app.exec_()


if __name__ == "__main__":
    main()
