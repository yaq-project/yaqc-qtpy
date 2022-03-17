__all__ = ["Float"]


import time
from functools import partial
from typing import Dict, Tuple, Callable

import qtypes
import qtpy

from ._disconnect import disconnect

signals: Dict[int, Tuple[qtpy.QtCore.Signal, Callable]] = {}


@disconnect(signals)
def value_updated(value, item, units):
    current = item.get()
    item.set({"value": qtypes._units.convert(value, units, current["units"])})


@disconnect(signals)
def limits_updated(value, item, units):
    current = item.get()
    lims = qtypes._units.convert(value, units, current["units"])
    item.set(
        {
            "minimum": min(lims),
            "maximum": max(lims),
        }
    )


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
    signals[id(item)] = []
    # signals and slots
    if hasattr(property, "units"):
        default_units = property.units()
        while not default_units.finished:
            time.sleep(0.01)
        default_units = default_units.result
    else:
        default_units = None
    item.set({"units": default_units})
    sig, func = property.updated, partial(value_updated, item=item, units=default_units)
    signals[id(item)].append((sig, func))
    sig.connect(func)
    if hasattr(property, "limits"):
        sig, func = property.limits.finished, partial(
            limits_updated, item=item, units=default_units
        )
        signals[id(item)].append((sig, func))
        sig.connect(func)
        property.limits()
    sig, func = item.edited, partial(set_daemon, default_units=default_units, property=property)
    signals[id(item)].append((sig, func))
    sig.connect(func)
    return item
