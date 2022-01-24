__all__ = ["Integer"]


import time
from functools import partial

import qtypes


def value_updated(value, item):
    item.set({"value": item.get()})


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
    property.updated.connect(partial(value_updated, item=item))
    if hasattr(property, "limits"):
        property.limits.finished.connect(partial(limits_updated, item=item))
        property.limits()
    item.edited.connect(partial(set_daemon, property=property))
    return item
