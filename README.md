# Pylint Secure Coding Standard Plugin

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pylint-secure-coding-standard?label=Python) [![PyPI version](https://badge.fury.io/py/pylint-secure-coding-standard.svg)](https://badge.fury.io/py/pylint-secure-coding-standard) [![CI Build](https://github.com/Takishima/pylint-secure-coding-standard/actions/workflows/ci.yml/badge.svg)](https://github.com/Takishima/pylint-secure-coding-standard/actions/workflows/ci.yml) [![CodeQL](https://github.com/Takishima/pylint-secure-coding-standard/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Takishima/pylint-secure-coding-standard/actions/workflows/codeql-analysis.yml) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Takishima/pylint-secure-coding-standard/main.svg)](https://results.pre-commit.ci/latest/github/Takishima/pylint-secure-coding-standard/main) [![Coverage Status](https://coveralls.io/repos/github/Takishima/pylint-secure-coding-standard/badge.svg?branch=main)](https://coveralls.io/github/Takishima/pylint-secure-coding-standard?branch=main)


pylint plugin that enforces some secure coding standards.

## Installation

    pip install pylint-secure-coding-standard

## Pylint codes

| Code  | Description                                                                                                  |
|-------|--------------------------------------------------------------------------------------------------------------|
| R8000 | Use `os.path.realpath()` instead of `os.path.abspath()` and `os.path.relpath()`                              |
| E8001 | Avoid using `exec()` and `eval()`                                                                            |
| E8002 | Avoid using `os.system()`                                                                                    |
| E8003 | Avoid using `shell=True` in subprocess functions or using functions that internally set this                 |
| R8004 | Avoid using `tempfile.mktemp()`, prefer `tempfile.mkstemp()` instead                                         |
| E8005 | Avoid using unsafe PyYAML loading functions                                                                  |
| E8006 | Avoid using `jsonpickle.decode()`                                                                            |
| C8007 | Avoid debug statement in production code                                                                     |
| C8008 | Avoid `assert` statements in production code                                                                 |
| R8009 | Use of builtin `open` for writing is discouraged in favor of `os.open` to allow for setting file permissions |
| E8010 | Avoid using `os.popen()` as it internally uses `subprocess.Popen` with `shell=True`                          |
| E8011 | Use of `shlex.quote()` should be avoided on non-POSIX platforms                                              |
| W8012 | Avoid using `os.open()` with unsafe permissions permissions                                                  |
| E8013 | Avoid using `pickle.load()` and `pickle.loads()`                                                             |
| E8014 | Avoid using `marshal.load()` and `marshal.loads()`                                                           |
| E8015 | Avoid using `shelve.open()`                                                                                  |
| W8016 | Avoid using `os.mkdir` and `os.makedirs` with unsafe file permissions                                        |
| W8017 | Avoid using `os.mkfifo` with unsafe file permissions                                                         |
| W8018 | Avoid using `os.mknod` with unsafe file permissions                                                          |
| W8019 | Avoid using `os.chmod` with unsafe permissions (W ^ X for group and others)                                  |


## Plugin configuration options

This plugin supports some configuration options that may either be specified directly on the command line with a flag
using the option name as `--name` or by specifying them in one of pylint's configuration files (ie. `pyproject.toml`,
`pylintrc`, etc.).

Available options:

| Option name    | Option type | Default value | Related error code |
|----------------|-------------|---------------|--------------------|
| os-open-mode   | mode-like   | 0 (off)       | W8012              |
| os-mkdir-mode  | mode-like   | 0 (off)       | E8016              |
| os-mkfifo-mode | mode-like   | 0 (off)       | E8017              |
| os-mknod-mode  | mode-like   | 0 (off)       | E8018              |


### Mode-like options

Mode-like options are configuration options for errors/warnings that relate to some function that accepts a `mode`
parameter (or similar) that control some file or directory permissions. For those kind of options, the plugin
understands a variety of values that must be specified as `string`. They will then be parsed into a list of allowed mode
values:

- Any positive, non-zero (octal or decimal) integer value specifies the maximum value for the mode value
- A comma-separated list of (octal or decimal) integers indicates the list of allowed mode values
- 'y', 'yes', 'true' (case-insensitive) will turn on the warnings using the default value of `0o755`
- 'n', 'no', 'false' (case-insensitive) will turn off the warnings

Example of values:
```toml
    [tool.pylint.plugins]
    os-open-mode = '0'            # check disabled
    os-open-mode = 'no'           # check disabled
    os-open-mode = '493'          # all modes from 0 to 493 (=0o755)
    os-open-mode = '0o755'        # all modes from 0 to 0o755
    os-open-mode = '0o755,'       # only 0o755 (notice the comma)
    os-open-mode = '0o644,0o755'  # only 0o644 and 0o755
```

You can also specify those options directly on the command line:

```sh
python3 -m pylint --load-plugins=pylint_secure_coding_standard --os-open-mode='0o755'
```

## Pre-commit hook

See [pre-commit](https://github.com/pre-commit/pre-commit) for instructions

Sample `.pre-commit-config.yaml`:

```yaml
  - repo: https://github.com/PyCQA/pylint/
    rev: pylint-2.6.0
    hooks:
    -   id: pylint
        args: [--load-plugins=pylint_secure_coding_standard]
        additional_dependencies: ['pylint-secure-coding-standard']
```
