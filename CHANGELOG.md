# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v1.5.0] - 2023-11-19

### Changed

- Changed minimum Python version to 3.8.X
- Requires Pylint 3.0

### Fixed

- Compatibility with Pylint 3.0

### Repository

- Replace most Python pre-commit hooks with [ruff](https://beta.ruff.rs/docs/)
- Update release drafting GitHub workflow
- Modify pull requests workflow to automatically update CHANGELOG file if it was created by pre-commit.ci
- Added some more pre-commit hooks:
  - doc8
  - codespell
  - yamllint
  - blacken-docs
- Update `thomaseizinger/create-pull-request` GitHub Action to v1.3.1
- Update `astral-sh/ruff-pre-commit` to v0.1.5
- Update `asottile/blacken-docs` hook to v1.16.0
- Update `codespell-project/codespell` hook to v2.2.6
- Update `Lucas-C/pre-commit-hooks` hook to v1.5.4
- Update `pre-commit/pre-commit-hooks` hook to v4.5.0
- Update `psf/black` hook to v23.11.0
- Update `yamllint` hook to v1.33.0
- Update GitHub Action `stefanzweifel/git-auto-commit-action` to v5

## [v1.4.1] - 2022-05-04

### Fixed

- Fixed uses of of `pylint.testutils.MessageTest` instead of `pylint.testutils.Message` for Pylint >= 2.12
- Fixed failing tests due to missing `ignore_position` argument to `assertAddsMessages()`

### Repository

- Update `black` hook to v22.3.0
- Update `check-manifest` hook to v0.48
- Update `isort` hook to v5.10.1
- Update `flake8` hook to v4.0.1
- Update `pre-commit/pre-commit-hooks` to v4.2.0
- Update `Lucas-C/pre-commit-hooks` hook to v1.2.0
- Update `dangoslen/changelog-enforcer` GitHub action to v3
- Update `thomaseizinger/create-pull-request` GitHub action to v1.2.2
- Update `thomaseizinger/keep-a-changelog-new-release` GitHub action to v1.3.0
- Update GitHub's CodeQL action to v2
- Update parse-changelog version to v0.4.7
- Fixed issue with release publishing GitHub workflow

## [v1.4.0] - 2021-07-29

### Added

- Added W8016 to warn when using `os.mkdir` and `os.makedir` with unsafe permissions (UNIX-only)
- Added W8017 to warn when using `os.mkfifo` with unsafe permissions (UNIX-only)
- Added W8018 to warn when using `os.mknod` with unsafe permissions (UNIX-only)
- Added W8019 to warn when using `os.chmod` with unsafe permissions (all except Windows)

### Updated

- Refactor configuration option parsing for mode-like options

### Fixed

- Critical typo for `msgs` attribute of the plugin class. This effectively rendered any previous version useless as
  pylint would not recognize the warning/error messages

### Repository

- Restrict running some GitHub actions when a pull request is merged

## [v1.3.1] - 2021-07-27

### Updated

- Update unit tests for `os.open()`

### Fixed

- Fix issue when processing keyword arguments for `os.open()`

### Repository

- Restrict running some GitHub actions only when pull requests are updated

## [v1.3.0] - 2021-07-26

### Added

- Add plugin option to control whether we favour `os.open` over the builtin `open`
- Added W8012 to warn when using `os.open` with unsafe permissions
- Added E8013 to avoid using `pickle.load` and `pickle.loads`
- Added E8014 to avoid using `marshal.load` and `marshal.loads`
- Added E8015 to avoid using `shelve.open`

### Fixed

- Fixed a few test function names

### Repository

- Update pre-commit hooks
- Update `thomaseizinger/create-pull-request` GiHub action

## [v1.2.1] - 2021-07-19

- Reworded E8003 and extend it to include a few more cases:
  - `subprocess.getoutput()`
  - `subprocess.getstatusoutput()`
  - `asyncio.create_subprocess_shell()`
  - `loop.subprocess_shell()`

## [v1.2.0] - 2021-07-19

### Added

- Added E8010 to avoid using `os.popen()` as it internally uses `subprocess.Popen` with `shell=True`
- Added E8011 to avoid using `shlex.quote()` on non-POSIX platforms.

## [v1.1.0] - 2021-07-02

### Added

- Added R8009 to prefer `os.open()` to the builtin `open` when in writing mode

### Repository

- Update pre-commit configuration

## [v1.0.0] - 2021-06-21

Initial release

[unreleased]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.5.0...HEAD
[v1.0.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/375145a3dec096ff4e33901ef749a1a9a6f4edc6...v1.0.0
[v1.1.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.0.0...v1.1.0
[v1.2.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.1.0...v1.2.0
[v1.2.1]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.2.0...v1.2.1
[v1.3.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.2.1...v1.3.0
[v1.3.1]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.3.0...v1.3.1
[v1.4.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.3.1...v1.4.0
[v1.4.1]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.4.0...v1.4.1
[v1.5.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.4.1...v1.5.0
