__all__ = ["Enum"]


import time
from functools import partial

import qtypes


def value_updated(value, item, units):
    current = item.get()
    item.set({"value": qtypes._units.convert(value, units, current["units"])})


def options_updated(value, item):
    item.set({"allowed": value})


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
    property.options.finished.connect(partial(options_updated, item=item))
    property.options()
    item.edited.connect(partial(set_daemon, property=property))
    return item
