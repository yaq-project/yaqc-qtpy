__all__ = ["Enum"]


import time
from functools import partial
from typing import Dict, Tuple, Callable

import qtypes
import qtpy

from ._disconnect import disconnect

signals: Dict[int, Tuple[qtpy.QtCore.Signal, Callable]] = {}


@disconnect(signals)
def options_updated(value, item):
    item.set({"allowed": value})


@disconnect(signals)
def value_updated(value, item):
    item.set({"value": value})


def set_daemon(value, property):
    property(value["value"])


def Enum(key, property, qclient):
    # disabled
    if property._property.get("setter", None):
        disabled = False
    else:
        disabled = True
    # make item
    item = qtypes.Enum(disabled=disabled, label=key)
    # signals and slots
    sig, func = property.updated, partial(value_updated, item=item)
    signals[id(item)].append((sig, func))
    sig.connect(func)
    sig, func = property.options.finished, partial(options_updated, item=item)
    signals[id(item)].append((sig, func))
    sig.connect(func)
    sig, func = item.edited, partial(set_daemon, property=property)
    signals[id(item)].append((sig, func))
    sig.connect(func)
    property.options()
    return item
