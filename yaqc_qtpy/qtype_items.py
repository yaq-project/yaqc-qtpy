
import qtypes


def property_item(key, property, qclient):
    # disabled
    if property._property.get("setter", None):
        disabled = False
    else:
        disabled = True
    # widgets
    if property.type == "boolean":
        pass   # TODO:
    elif property.type in ["double"]:

        def value_updated(value, item):
            item.set({"value": value})

        def units_updated(units, item):
            item.set({"units": units})

        item = qtypes.Float(disabled=disabled, label=key, value={"value": 5})
        from functools import partial
        qclient.properties[key].updated.connect(partial(value_updated, item=item))
        qclient.properties[key].units.finished.connect(partial(units_updated, item=item))
        qclient.properties[key].units()



    elif property.type == "string" and "options_getter" in property._property.keys():
        return
        allowed_values = getattr(self.client, property._property["options_getter"])()
        item = qtypes.Enum(disabled=disabled, label=key)
    elif property.type == "string":
        item = qtypes.String(disabled=disabled, name=key)
    else:
        pass
    # updated signal
    #property.updated.connect(functools.partial(self._on_property_updated, key=key))
    return item



def append_properties(qclient, root):
    # TODO: move to own file
    for key, property in qclient.properties.items():
        item = property_item(key, property, qclient)
        if item:
            root.append(item)



def append_card_item(qclient, root):
    # TODO: move to own file
    # busy
    busy = qtypes.Bool(f"{qclient.id()['name']}", disabled=True)
    qclient.busy_signal.connect(busy.set_value)
    root.append(busy)
    # host:port
    busy.append(qtypes.String(label="host:port", disabled=True, value={"value": f"{qclient.host}:{qclient.port}"}))
    # properties
    append_properties(qclient, busy)
    # advanced button
    advanced_button = qtypes.Button(label="")
    busy.append(advanced_button)
    advanced_button._widget.setText("view advanced menu")
