# yaqc-qtpy

[![PyPI](https://img.shields.io/pypi/v/yaqc-qtpy)](https://pypi.org/project/yaqc-qtpy)
[![Conda](https://img.shields.io/conda/vn/conda-forge/yaqc-qtpy)](https://anaconda.org/conda-forge/yaqc-qtpy)
[![yaq](https://img.shields.io/badge/framework-yaq-orange)](https://yaq.fyi/)
[![black](https://img.shields.io/badge/code--style-black-black)](https://black.readthedocs.io/)
[![ver](https://img.shields.io/badge/calver-YYYY.M.MICRO-blue)](https://calver.org/)
[![log](https://img.shields.io/badge/change-log-informational)](https://gitlab.com/yaq/yaqc-qtpy/-/blob/main/CHANGELOG.md)

Tooling for building simple yaq clients using qtpy.

## application usage

TODO: screenshot

```bash
yaqd list --format json | yaqc-qtpy -
```

### entry point

DOCUMENTATION TODO

## library usage

yaqc-qtpy can be used as a Python package for those building Qt-based interfaces to yaq.

### qclient

DOCUMENTATION TODO

### item generators

The yaqc-qtpy application uses the [qtypes](https://gitlab.com/yaq/qtypes) widget tooling.
Other developers who are using qtypes can benefit from the built in item generators.

DOCUMENTATION TODO

#### `append_properties`

DOCUMENTATION TODO

#### `append_card_item`

DOCUMENTATION TODO