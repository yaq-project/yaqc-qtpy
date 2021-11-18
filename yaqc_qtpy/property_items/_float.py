__all__ = ["Float"]


import time
from functools import partial

import qtypes


def value_updated(value, item, units):
    current = item.get()
    item.set({"value": qtypes._units.convert(value, units, current["units"])})


def set_daemon(value, default_units, property):
    raw = qtypes._units.convert(value["value"], value["units"], default_units)
    property(raw)


def Float(key, property, qclient):
    # disabled
    if property._property.get("setter", None):
        disabled = False
    else:
        disabled = True
    # make item
    item = qtypes.Float(disabled=disabled, label=key)
    # signals and slots
    default_units = property.units()
    while not default_units.finished:
        time.sleep(0.01)
    property.updated.connect(partial(value_updated, item=item, units=default_units.result))
    item.set({"units": default_units.result})
    item.edited.connect(partial(set_daemon, default_units=default_units.result, property=property))
    return item
