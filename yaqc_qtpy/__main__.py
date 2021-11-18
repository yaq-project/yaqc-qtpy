import sys

import click
import json
from qtpy import QtWidgets

from ._main_window import MainWindow
from .__version__ import __version__


@click.command()
@click.argument("input", type=click.File("rb"))
def main(input):
    input = json.load(input)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(input)
    window.show()
    window.showMaximized()
    app.exec_()


if __name__ == "__main__":
    main()
