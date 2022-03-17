# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

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


[Unreleased]: https://gitlab.com/yaq/yaqc-qtpy/-/compare/v2022.3.0...main
[2022.3.0]: https://gitlab.com/yaq/yaqc-qtpy/-/compare/v2022.2.1...v2022.3.0
[2022.2.1]: https://gitlab.com/yaq/yaqc-qtpy/-/compare/v2022.2.0...v2022.2.1
[2022.2.0]: https://gitlab.com/yaq/yaqc-qtpy/-/compare/v2022.1.1...v2022.2.0
[2022.1.1]: https://gitlab.com/yaq/yaqc-qtpy/-/compare/v2022.1.0...v2022.1.1
[2022.1.0]: https://gitlab.com/yaq/yaqc-qtpy/-/compare/v2021.12.0...v2022.1.0
[2021.12.0]: https://gitlab.com/yaq/yaqc-qtpy/-/compare/v2021.11.0...v2021.12.0
[2021.11.0]: https://gitlab.com/yaq/yaqc-qtpy/-/tags/v2021.11.0
