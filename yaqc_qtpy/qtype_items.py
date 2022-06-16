import time

import qtypes

from . import property_items, QClient


def append_properties(qclient, root, only_hinted=False):
    # TODO: move to own file
    for key, property in qclient.properties.items():
        if only_hinted and property.control_kind == "normal":
            continue
        if property.type == "boolean":
            root.append(property_items.Boolean(key, property, qclient))
        elif property.type in ["float", "double"]:
            root.append(property_items.Float(key, property, qclient))
        elif property.type == "string" and "options_getter" in property._property.keys():
            root.append(property_items.Enum(key, property, qclient))
        elif property.type == "string":
            root.append(property_items.String(key, property, qclient))
        elif property.type == "int":
            root.append(property_items.Integer(key, property, qclient))
        elif qclient._client._named_types.get(property.type, {}).get("type") == "enum":
            schema = qclient._client._named_types[property.type]
            root.append(property_items.Enum(key, property, qclient, schema["symbols"]))
        else:
            pass


def append_card_item(qclient, root, position=-1):
    # TODO: move to own file
    # busy
    busy = qtypes.Bool(f"{qclient.id()['name']}", disabled=True)
    qclient.busy_signal.connect(busy.set_value)
    busy.qclient = qclient
    root.insert(position, busy)
    # host:port
    busy.append(
        qtypes.String(label="host:port", disabled=True, value=f"{qclient.host}:{qclient.port}")
    )
    # properties
    append_properties(qclient, busy, only_hinted=True)
    # advanced button
    advanced_button = qtypes.Button(label="")
    busy.append(advanced_button)
    advanced_button.set({"text": "view advanced menu"})
    if hasattr(qclient, "get_dependent_hardware"):
        dependents = qtypes.Null("Dependents")
        busy.append(dependents)
        task = qclient.get_dependent_hardware()
        while not task.finished:
            time.sleep(0.01)
        for key, host_port in task.result.items():
            try:
                host, port = host_port.split(":", 1)
                if host in ("localhost", "127.0.0.1"):
                    host = qclient.host
                dep_client = QClient(host, int(port))
                append_card_item(dep_client, dependents)
            except:
                dependents.append(qtypes.String(key, disabled=True, value="offline"))
    return busy
