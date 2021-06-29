# -*- coding: utf-8 -*-
# Copyright 2021 Damien Nguyen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main file for the pylint_secure_coding_standard plugin"""

import astroid

from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker


# ==============================================================================


def _is_os_system_call(node):
    return (
        isinstance(node.func, astroid.Attribute)
        and isinstance(node.func.expr, astroid.Name)
        and node.func.expr.name == 'os'
        and node.func.attrname == 'system'
    )


def _is_os_path_call(node):
    return (
        isinstance(node.func, astroid.Attribute)
        and (
            (isinstance(node.func.expr, astroid.Name) and node.func.expr.name == 'op')
            or (
                isinstance(node.func.expr, astroid.Attribute)
                and node.func.expr.attrname == 'path'
                and isinstance(node.func.expr.expr, astroid.Name)
                and node.func.expr.expr.name == 'os'
            )
        )
        and node.func.attrname in ('abspath', 'relpath')
    )


def _is_builtin_open_for_writing(node):
    if isinstance(node.func, astroid.Name) and node.func.name == 'open':
        mode = ''
        if len(node.args) > 1:
            if isinstance(node.args[1], astroid.Name):
                return True  # variable -> to be on the safe side, flag as inappropriate
            if isinstance(node.args[1], astroid.Const):
                mode = node.args[1].value
        elif node.keywords:
            for keyword in node.keywords:
                if keyword.arg == 'mode':
                    if not isinstance(keyword.value, astroid.Const):
                        return True  # variable -> to be on the safe side, flag as inappropriate
                    mode = keyword.value.value
                    break

        if any(m in mode for m in 'awx'):
            # open(..., "w")
            # open(..., "wb")
            # open(..., "a")
            # open(..., "x")
            return True
    return False


def _is_subprocess_shell_true_call(node):
    if (
        isinstance(node.func, astroid.Attribute)
        and isinstance(node.func.expr, astroid.Name)
        and node.func.expr.name in ('subprocess', 'sp')
    ):
        if node.keywords:
            for keyword in node.keywords:
                if keyword.arg == 'shell' and isinstance(keyword.value, astroid.Const) and bool(keyword.value.value):
                    return True

        if len(node.args) > 8 and isinstance(node.args[8], astroid.Const) and bool(node.args[8].value):
            return True
    return False


def _is_pdb_call(node):
    if isinstance(node.func, astroid.Attribute):
        if isinstance(node.func.expr, astroid.Name) and node.func.expr.name == 'pdb':
            # pdb.func()
            return True
    if isinstance(node.func, astroid.Name):
        if node.func.name == 'Pdb':
            # Pdb()
            return True
    return False


def _is_mktemp_call(node):
    if isinstance(node.func, astroid.Attribute):
        if node.func.attrname == 'mktemp':
            # tempfile.mktemp()
            # xxxx.mktemp()
            return True
    if isinstance(node.func, astroid.Name):
        if node.func.name == 'mktemp':
            # mktemp()
            return True
    return False


def _is_yaml_unsafe_call(node):
    _safe_loaders = ('BaseLoader', 'SafeLoader')
    _unsafe_loaders = ('Loader', 'UnsafeLoader', 'FullLoader')
    if (
        isinstance(node.func, astroid.Attribute)
        and isinstance(node.func.expr, astroid.Name)
        and node.func.expr.name == 'yaml'
    ):
        if node.func.attrname in ('unsafe_load', 'full_load'):
            # yaml.full_load()
            # yaml.unsafe_load()
            return True
        if node.func.attrname == 'load' and node.keywords:
            for keyword in node.keywords:
                if keyword.arg == 'Loader' and isinstance(keyword.value, astroid.Name):
                    if keyword.value.name in _unsafe_loaders:
                        # yaml.load(x, Loader=Loader), yaml.load(x, Loader=UnsafeLoader),
                        # yaml.load(x, Loader=FullLoader)
                        return True
                    if keyword.value.name in _safe_loaders:
                        # yaml.load(x, Loader=BaseLoader), yaml.load(x, Loader=SafeLoader),
                        return False
        elif node.func.attrname == 'load':
            if len(node.args) < 2 or (isinstance(node.args[1], astroid.Name) and node.args[1].name in _unsafe_loaders):
                # yaml.load(x)
                # yaml.load(x, Loader), yaml.load(x, UnsafeLoader), yaml.load(x, FullLoader)
                return True

    if isinstance(node.func, astroid.Name):
        if node.func.name in ('unsafe_load', 'full_load'):
            # unsafe_load()
            # full_load()
            return True
    return False


def _is_jsonpickle_encode_call(node):
    if isinstance(node.func, astroid.Attribute):
        if (
            isinstance(node.func.expr, astroid.Name)
            and node.func.expr.name == 'jsonpickle'
            and node.func.attrname == 'decode'
        ):
            return True
    return False


# ==============================================================================


class SecureCodingStandardChecker(BaseChecker):
    """Plugin class"""

    __implements__ = IAstroidChecker

    name = 'secure-coding-standard'
    priority = -1

    msg = {
        'R8000': (
            'Use `os.path.realpath()` instead of `os.path.abspath()` and `os.path.relpath()`',
            'replace-os-relpath-abspath',
            'Use of `os.path.abspath()` and `os.path.relpath()` should be avoided in favor of `os.path.realpath()`',
        ),
        'E8001': (
            'Avoid using `exec()` and `eval()`',
            'avoid-eval-exec',
            'Use of `eval()` and `exec()` represent a security risk and should be avoided',
        ),
        'E8002': ('Avoid using `os.sytem()`', 'avoid-os-system', 'Use of `os.system()` should be avoided'),
        'E8003': (
            'Avoid using `shell=True` when calling `subprocess` functions',
            'avoid-shell-true',
            'Use of `shell=True` in subprocess functions should be avoided',
        ),
        'R8004': (
            'Avoid using `tempfile.mktemp()`, prefer `tempfile.mkstemp()` instead',
            'replace-mktemp',
            'Use of `tempfile.mktemp()` should be avoided, prefer `tempfile.mkstemp()`',
        ),
        'E8005': (
            'Avoid using unsafe PyYAML loading functions',
            'avoid-yaml-unsafe-load',
            'Use of `yaml.load()` should be avoided, prefer `yaml.safe_load()` or `yaml.load(xxx, Loader=SafeLoader)`',
        ),
        'E8006': (
            'Avoid using `jsonpickle.decode()`',
            'avoid-jsonpickle-decode',
            'Use of `jsonpickle.decode()` should be avoided',
        ),
        'C8007': (
            'Avoid debug statement in production code',
            'avoid-debug-stmt',
            'Use of debugging code shoud not be present in production code (e.g. `import pdb`)',
        ),
        'C8008': (
            'Avoid `assert` statements in production code',
            'avoid-assert',
            '`assert` statements should not be present in production code',
        ),
        'R8005': (
            'Avoid builtin open() when writing to files, prefer os.open()',
            'replace-builtin-open',
            'Use of builtin `open` for writing is discouraged in favor of `os.open` to allow for setting file '
            'permissions',
        ),
    }

    options = {}

    def visit_call(self, node):
        """
        Visitor method called for astroid.Call nodes
        """
        if _is_pdb_call(node):
            self.add_message('avoid-debug-stmt', node=node)
        elif _is_mktemp_call(node):
            self.add_message('replace-mktemp', node=node)
        elif _is_yaml_unsafe_call(node):
            self.add_message('avoid-yaml-unsafe-load', node=node)
        elif _is_jsonpickle_encode_call(node):
            self.add_message('avoid-jsonpickle-decode', node=node)
        elif _is_os_system_call(node):
            self.add_message('avoid-os-system', node=node)
        elif _is_os_path_call(node):
            self.add_message('replace-os-relpath-abspath', node=node)
        elif _is_subprocess_shell_true_call(node):
            self.add_message('avoid-shell-true', node=node)
        elif _is_builtin_open_for_writing(node):
            self.add_message('replace-builtin-open', node=node)
        elif isinstance(node.func, astroid.Name) and (node.func.name in ('eval', 'exec')):
            self.add_message('avoid-eval-exec', node=node)

    def visit_import(self, node):
        """
        Visitor method called for astroid.Import nodes
        """
        for (name, _) in node.names:
            if name == 'pdb':
                # import pdb
                # import pdb as xxx
                self.add_message('avoid-debug-stmt', node=node)

    def visit_importfrom(self, node):
        """
        Visitor method called for astroid.ImportFrom nodes
        """
        if node.modname == 'pdb':
            self.add_message('avoid-debug-stmt', node=node)
        elif node.modname == 'tempfile' and [name for (name, _) in node.names if name == 'mktemp']:
            self.add_message('replace-mktemp', node=node)
        elif node.modname in ('os.path', 'op') and [name for (name, _) in node.names if name in ('relpath', 'abspath')]:
            self.add_message('replace-os-relpath-abspath', node=node)
        elif node.modname == 'os' and [name for (name, _) in node.names if name == 'system']:
            self.add_message('avoid-os-system', node=node)

    def visit_with(self, node):
        """
        Visitor method called for astroid.With nodes
        """
        for item in node.items:
            if item and isinstance(item[0], astroid.Call) and _is_builtin_open_for_writing(item[0]):
                self.add_message('replace-builtin-open', node=node)

    def visit_assert(self, node):
        """
        Visitor method called for astroid.Assert nodes
        """
        self.add_message('avoid-assert', node=node)


def register(linter):  # pragma: no cover
    """
    Function to register the plugin to Pylint
    """
    linter.register_checker(SecureCodingStandardChecker(linter))
