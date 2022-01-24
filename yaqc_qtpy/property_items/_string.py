__all__ = ["String"]


import time
from functools import partial

import qtypes


def value_updated(value, item):
    item.set({"value": item.get()})


def set_daemon(value, property):
    property(value["value"])


def String(key, property, qclient):
    # disabled
    if property._property.get("setter", None):
        disabled = False
    else:
        disabled = True
    # make item
    item = qtypes.String(disabled=disabled, label=key)
    # signals and slots
    property.updated.connect(partial(value_updated, item=item))
    item.edited.connect(partial(set_daemon, property=property))
    return item
