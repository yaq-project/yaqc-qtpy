import time

import qtypes

from . import property_items


def append_properties(qclient, root, only_hinted=False):
    # TODO: move to own file
    for key, property in qclient.properties.items():
        if only_hinted and property.control_kind == "normal":
            continue
        if property.type == "boolean":
            continue
            item = qtypes.Bool(disabled=disabled, label=key)
        elif property.type in ["double"]:
            root.append(property_items.Float(key, property, qclient))
        elif property.type == "string" and "options_getter" in property._property.keys():
            root.append(property_items.Enum(key, property, qclient))
        elif property.type == "string":
            continue
            item = qtypes.String(disabled=disabled, name=key)
        else:
            pass


def append_card_item(qclient, root):
    # TODO: move to own file
    # busy
    busy = qtypes.Bool(f"{qclient.id()['name']}", disabled=True)
    qclient.busy_signal.connect(busy.set_value)
    root.append(busy)
    # host:port
    busy.append(
        qtypes.String(
            label="host:port", disabled=True, value={"value": f"{qclient.host}:{qclient.port}"}
        )
    )
    # properties
    append_properties(qclient, busy, only_hinted=True)
    # advanced button
    advanced_button = qtypes.Button(label="")
    busy.append(advanced_button)
    advanced_button._widget.setText("view advanced menu")
