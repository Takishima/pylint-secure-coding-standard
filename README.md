# Pylint Secure Coding Standard Plugin

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pylint-secure-coding-standard?label=Python) [![PyPI version](https://badge.fury.io/py/pylint-secure-coding-standard.svg)](https://badge.fury.io/py/pylint-secure-coding-standard) [![CI Build](https://github.com/Takishima/pylint-secure-coding-standard/actions/workflows/ci.yml/badge.svg)](https://github.com/Takishima/pylint-secure-coding-standard/actions/workflows/ci.yml) [![CodeQL](https://github.com/Takishima/pylint-secure-coding-standard/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Takishima/pylint-secure-coding-standard/actions/workflows/codeql-analysis.yml) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Takishima/pylint-secure-coding-standard/main.svg)](https://results.pre-commit.ci/latest/github/Takishima/pylint-secure-coding-standard/main) [![Coverage Status](https://coveralls.io/repos/github/Takishima/pylint-secure-coding-standard/badge.svg?branch=main)](https://coveralls.io/github/Takishima/pylint-secure-coding-standard?branch=main)


pylint plugin that enforces some secure coding standards.

## Installation

    pip install pylint-secure-coding-standard

## Pylint codes

| Code  | Description                                                                     |
|-------|---------------------------------------------------------------------------------|
| R8000 | Use `os.path.realpath()` instead of `os.path.abspath()` and `os.path.relpath()` |
| E8001 | Avoid using `exec()` and `eval()`                                               |
| E8002 | Avoid using `os.sytem()`                                                        |
| E8003 | Avoid using `shell=True` when calling `subprocess` functions                    |
| R8004 | Avoid using `tempfile.mktemp()`, prefer `tempfile.mkstemp()` instead            |
| E8005 | Avoid using unsafe PyYAML loading functions                                     |
| E8006 | Avoid using `jsonpickle.decode()`                                               |
| C8007 | Avoid debug statement in production code                                        |
| C8008 | Avoid `assert` statements in production code                                    |


## Pre-commit hook

See [pre-commit](https://github.com/pre-commit/pre-commit) for instructions

Sample `.pre-commit-config.yaml`:

```yaml
  - repo: https://github.com/pycqa/pylint
    rev: pylint-2.6.0
    hooks:
    -   id: pylint
        args: [--load-plugins=pylint_secure_coding_standard]
        additional_dependencies: ['pylint-secure-coding-standard']
```
