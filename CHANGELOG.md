# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.2.0...HEAD

[1.2.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.1.0...v1.2.0

[1.1.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.0.0...v1.1.0

[1.0.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/375145a3dec096ff4e33901ef749a1a9a6f4edc6...v1.0.0
