__all__ = ["Integer"]


import time
from functools import partial
from typing import Dict, Tuple, Callable

import qtypes
import qtpy


from ._disconnect import disconnect

signals: Dict[int, Tuple[qtpy.QtCore.Signal, Callable]] = {}


@disconnect(signals)
def value_updated(value, item):
    item.set({"value": value})


@disconnect(signals)
def limits_updated(value, item):
    item.set({"minimum": value[0], "maximum": value[1]})


def set_daemon(value, property):
    property(value["value"])


def Integer(key, property, qclient):
    # disabled
    if property._property.get("setter", None):
        disabled = False
    else:
        disabled = True
    # make item
    item = qtypes.Integer(disabled=disabled, label=key)
    # signals and slots
    sig, func = property.updated, partial(value_updated, item=item)
    signals[id(item)].append((sig, func))
    sig.connect(func)
    if hasattr(property, "limits"):
        sig, func = property.limits.finished, partial(limits_updated, item=item)
        signals[id(item)].append((sig, func))
        sig.connect(func)
        property.limits()
    sig, func = item.edited, partial(set_daemon, property=property)
    signals[id(item)].append((sig, func))
    sig.connect(func)
    return item
