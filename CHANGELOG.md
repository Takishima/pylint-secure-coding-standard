# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Build Python 3 only wheels (`py3-none-any`) instead of universal `py2.py3` ones

### Repository

- Validate the version given to the release drafting workflow (the leading `v` is optional and normalised, existing
  tags/branches and an empty `[Unreleased]` section are rejected)
- Replace the `stefanzweifel/git-auto-commit-action` and `thomaseizinger/create-pull-request` GitHub Actions with plain
  `git` and `gh` commands in the release drafting workflow
- Split the release publishing workflow into separate build, PyPI upload and GitHub release jobs with minimal
  permissions; the GitHub release is now only created once the PyPI upload succeeded
- Build the release from the merged commit using `SETUPTOOLS_SCM_PRETEND_VERSION` instead of a temporary Git tag
- Fix the pre-release detection when creating the GitHub release
- Deduce the next version from the CHANGELOG in the release drafting workflow (`auto`, `patch`, `minor` or `major`
  instead of an explicit version)
- Open the release pull request automatically every Monday if user-facing changes are waiting to be released
- Delete the release branch once the release is published
- Allow uploading to PyPI using trusted publishing

## [v1.6.0] - 2026-11-21

### Changed

- Drop support for Python 3.8 and 3.9 (end-of-life); Python 3.10 is now the minimum version
- Add official support for Python 3.12, 3.13, 3.14 and 3.15

### Repository

- Update `action/setup-python` GitHub Action to v7
- Update `action/checkout` GitHub Action to v7
- Update `github/codeql-action` GitHub Actions to v4
- Update `thomaseizinger/create-pull-request` GitHub Action to v1.4.0
- Update `stefanzweifel/git-auto-commit-action` GitHub Action to v7
- Update `EndBug/add-and-commit` GitHub Action to v11
- Run CI for Python 3.10 to 3.15 on Linux, Windows and macOS
- Upload coverage data using the `coverallsapp/github-action` GitHub Action
- Group all GitHub Actions updates from Dependabot into a single pull request
- Avoid shell injection from pull request data in GitHub workflows
- Restrict the default `GITHUB_TOKEN` permissions in all GitHub workflows
- Update `adrienverge/yamllint.git` hook to v1.38.0
- Update `asottile/blacken-docs` hook to v1.20.0
- Update `astral-sh/ruff-pre-commit` hook to v0.17.5
- Update `codespell-project/codespell` hook to v2.4.3
- Update `Lucas-C/pre-commit-hooks` hook to v1.5.6
- Update `pre-commit/pre-commit-hooks` hook to v6.0.0
- Remove the `doc8` pre-commit hook (no reStructuredText files in the repository)
- Run the `ruff` linter hook before the formatter hook and use the new `ruff-check` hook id
- Remove deprecated and removed settings from the `ruff` configuration
- Fix the release version passed to `parse-changelog` in the format workflow for release and hotfix branches

## [v1.5.1] - 2023-12-15

### Fixed

- Configuration options retrieval on Pylint 3
- GitHub workflows

### Repository

- Update `adrienverge/yamllint` hook to v1.33.0
- Update `astral-sh/ruff-pre-commit` hook to v0.1.8

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

[unreleased]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.6.0...HEAD
[v1.0.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/375145a3dec096ff4e33901ef749a1a9a6f4edc6...v1.0.0
[v1.1.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.0.0...v1.1.0
[v1.2.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.1.0...v1.2.0
[v1.2.1]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.2.0...v1.2.1
[v1.3.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.2.1...v1.3.0
[v1.3.1]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.3.0...v1.3.1
[v1.4.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.3.1...v1.4.0
[v1.4.1]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.4.0...v1.4.1
[v1.5.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.4.1...v1.5.0
[v1.5.1]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.5.0...v1.5.1
[v1.6.0]: https://github.com/Takishima/pylint-secure-coding-standard/compare/v1.5.1...v1.6.0
