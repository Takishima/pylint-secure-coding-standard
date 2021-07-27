# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.1] - 2021-07-27

### Updated

-   Update unit tests for `os.open()`

### Fixed

-   Fix issue when processing keyword arguments for `os.open()`

### Repository

-   Restrict running some GitHub actions only when pull requests are updated

## [1.3.0] - 2021-07-26

### Added

-   Add plugin option to control whether we favour `os.open` over the builtin `open`
-   Added W8012 to warn when using `os.open` with unsafe permissions
-   Added E8013 to avoid using `pickle.load` and `pickle.loads`
-   Added E8014 to avoid using `marshal.load` and `marshal.loads`
-   Added E8015 to avoid using `shelve.open`

### Fixed

-   Fixed a few test function names

### Repository

-   Update pre-commit hooks
-   Update `thomaseizinger/create-pull-request` GiHub action

## [1.2.1] - 2021-07-19

-   Reworded E8003 and extend it to include a few more cases:
    -   `subprocess.getoutput()`
    -   `subprocess.getstatusoutput()`
    -   `asyncio.create_subprocess_shell()`
    -   `loop.subprocess_shell()`

## [1.2.0] - 2021-07-19

### Added

-   Added E8010 to avoid using `os.popen()` as it internally uses `subprocess.Popen` with `shell=True`
-   Added E8011 to avoid using `shlex.quote()` on non-POSIX platforms.

## [1.1.0] - 2021-07-02

### Added

-   Added R8009 to prefer `os.open()` to the builtin `open` when in writing mode

### Repository

-   Update pre-commit configuration

## [1.0.0] - 2021-06-21

Initial release

[Unreleased]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.3.1...HEAD

[1.3.1]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.3.0...v1.3.1

[1.3.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.2.1...v1.3.0

[1.2.1]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.2.0...v1.2.1

[1.2.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.1.0...v1.2.0

[1.1.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.0.0...v1.1.0

[1.0.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/375145a3dec096ff4e33901ef749a1a9a6f4edc6...v1.0.0
