# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [2022.6.0]

### Changed
- extensive refactor for new qtypes
- better plotting behavior for NaNs

## [2022.4.0]

### Added
- Hidden items list to help organize "important" daemons
- Items with dependent daemons show them in a collapsed list

### Changed
- Items are sorted by their name

### Fixed
- Ensure empty lists for signal/slot tuples are made before appending to them

## [2022.3.1]

### Fixed
- string and boolean property items now update correctly

## [2022.3.0]

### Added
- only three main widgets are kept in memory at once
- has-sensor window only updates if measurement_id has changed

### Fixed
- Use nanmin/nanmax for additional plotting over min/max
- Ensure min/max make sense when units change (i.e. min is less than max)

## [2022.2.1]

### Fixed
- behavior of limits with unit changes on float properties

## [2022.2.0]

### Fixed
- re fix enum property value updating

## [2022.1.1]

### Fixed
- enum property updates value properly

## [2022.1.0]

### Added
- boolean properties support
- integer properties support
- string properties support

### Fixed
- float properties without units were crashing program

## [2021.12.0]

### Added
- reconnect signal fires when reconnects occur
- Console widget tab
- is-sensor-widget

### Changed
- Default launch with no arguments gets all daemons in yaqd-control cache
- Allow for offline devices (placeholder tree item)
- overhauled has-position-widget
- Loading of plugin group name uses `_` instead of `-` due to restrictions in namespace

## [2021.11.0]

### Added
- initial release


[Unreleased]: https://github.com/yaq/yaqc-qtpy/compare/v2022.6.0...main
[2022.6.0]: https://github.com/yaq/yaqc-qtpy/compare/v2022.4.0...v2022.6.0
[2022.4.0]: https://github.com/yaq/yaqc-qtpy/compare/v2022.3.1...v2022.4.0
[2022.3.1]: https://github.com/yaq/yaqc-qtpy/compare/v2022.3.0...v2022.3.1
[2022.3.0]: https://github.com/yaq/yaqc-qtpy/compare/v2022.2.1...v2022.3.0
[2022.2.1]: https://github.com/yaq/yaqc-qtpy/compare/v2022.2.0...v2022.2.1
[2022.2.0]: https://github.com/yaq/yaqc-qtpy/compare/v2022.1.1...v2022.2.0
[2022.1.1]: https://github.com/yaq/yaqc-qtpy/compare/v2022.1.0...v2022.1.1
[2022.1.0]: https://github.com/yaq/yaqc-qtpy/compare/v2021.12.0...v2022.1.0
[2021.12.0]: https://github.com/yaq/yaqc-qtpy/compare/v2021.11.0...v2021.12.0
[2021.11.0]: https://github.com/yaq/yaqc-qtpy/tags/v2021.11.0
