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

"""Main file for the pylint_secure_coding_standard plugin."""

import platform

import astroid
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker

# ==============================================================================
# Helper functions


def _is_posix():
    """Return True if the current system is POSIX-compatible."""
    # NB: we could simply use `os.name` instead of `platform.system()`. However, that solution would be difficult to
    #     test using `mock` as a few modules (like `pytest`) actually use it internally...
    return platform.system() in ('Linux', 'Darwin')


# ==============================================================================


def _is_function_call(node, module, function):
    if not isinstance(function, (list, tuple)):
        function = (function,)
    return (
        isinstance(node.func, astroid.Attribute)
        and isinstance(node.func.expr, astroid.Name)
        and node.func.expr.name == module
        and node.func.attrname in function
    )


# ------------------------------------------------------------------------------


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
            # Cover:
            #  * open(..., "w")
            #  * open(..., "wb")
            #  * open(..., "a")
            #  * open(..., "x")
            return True
    return False


def _is_os_open_allowed_mode(node, allowed_modes):
    mode = None
    flags = None  # pylint: disable=unused-variable
    if len(node.args) > 1 and isinstance(node.args[1], (astroid.Attribute, astroid.BinOp)):
        # Cover:
        #  * os.open(xxx, os.O_WRONLY)
        #  * os.open(xxx, os.O_WRONLY | os.O_CREATE)
        #  * os.open(xxx, os.O_WRONLY | os.O_CREATE | os.O_FSYNC)
        flags = node.args[1]
    if len(node.args) > 2 and isinstance(node.args[2], astroid.Const):
        mode = node.args[2].value
    elif node.keywords:
        for keyword in node.keywords:
            if keyword.arg == 'flags' and isinstance(keyword.value, (astroid.Attribute, astroid.BinOp)):
                flags = keyword.value  # pylint: disable=unused-variable # noqa: F841
            if keyword.arg == 'mode' and isinstance(keyword.value, astroid.Const):
                mode = keyword.value.value
                break
    if mode is not None:
        # TODO: condition check on the flags value if present (ie. ignore if read-only)
        return mode in allowed_modes

    # NB: default to True in all other cases
    return True


def _is_shell_true_call(node):
    if not (isinstance(node.func, astroid.Attribute) and isinstance(node.func.expr, astroid.Name)):
        return False

    # subprocess module
    if node.func.expr.name in ('subprocess', 'sp'):
        if node.func.attrname in ('call', 'check_call', 'check_output', 'Popen', 'run'):
            if node.keywords:
                for keyword in node.keywords:
                    if (
                        keyword.arg == 'shell'
                        and isinstance(keyword.value, astroid.Const)
                        and bool(keyword.value.value)
                    ):
                        return True

            if len(node.args) > 8 and isinstance(node.args[8], astroid.Const) and bool(node.args[8].value):
                return True

        if node.func.attrname in ('getoutput', 'getstatusoutput'):
            return True

    # asyncio module
    if (node.func.expr.name == 'asyncio' and node.func.attrname == 'create_subprocess_shell') or (
        node.func.expr.name == 'loop' and node.func.attrname == 'subprocess_shell'
    ):
        return True

    return False


def _is_pdb_call(node):
    if isinstance(node.func, astroid.Attribute):
        if isinstance(node.func.expr, astroid.Name) and node.func.expr.name == 'pdb':
            # Cover:
            #  * pdb.func()
            return True
    if isinstance(node.func, astroid.Name):
        if node.func.name == 'Pdb':
            # Cover:
            # * Pdb()
            return True
    return False


def _is_mktemp_call(node):
    if isinstance(node.func, astroid.Attribute):
        if node.func.attrname == 'mktemp':
            # Cover:
            #  * tempfile.mktemp()
            #  * xxxx.mktemp()
            return True
    if isinstance(node.func, astroid.Name):
        if node.func.name == 'mktemp':
            # Cover:
            #  * mktemp()
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
            # Cover:
            #  * yaml.full_load()
            #  * yaml.unsafe_load()
            return True
        if node.func.attrname == 'load' and node.keywords:
            for keyword in node.keywords:
                if keyword.arg == 'Loader' and isinstance(keyword.value, astroid.Name):
                    if keyword.value.name in _unsafe_loaders:
                        # Cover:
                        #  * yaml.load(x, Loader=Loader)
                        #  * yaml.load(x, Loader=UnsafeLoader)
                        #  * yaml.load(x, Loader=FullLoader)
                        return True
                    if keyword.value.name in _safe_loaders:
                        # Cover:
                        #  * yaml.load(x, Loader=BaseLoader)
                        #  * yaml.load(x, Loader=SafeLoader)
                        return False
        elif node.func.attrname == 'load':
            if len(node.args) < 2 or (isinstance(node.args[1], astroid.Name) and node.args[1].name in _unsafe_loaders):
                # Cover:
                #  * yaml.load(x)
                #  * yaml.load(x, Loader)
                #  * yaml.load(x, UnsafeLoader)
                #  * yaml.load(x, FullLoader)
                return True

    if isinstance(node.func, astroid.Name):
        if node.func.name in ('unsafe_load', 'full_load'):
            # Cover:
            #  * unsafe_load(...)
            #  * full_load(...)
            return True
    return False


# ==============================================================================


class SecureCodingStandardChecker(BaseChecker):
    """Plugin class."""

    DEFAULT_MAX_MODE = 0o755
    W8012_DISPLAY_MSG = 'Avoid using `os.open` with unsafe permissions permissions'

    __implements__ = (IAstroidChecker,)

    name = 'secure-coding-standard'
    options = (
        (
            'os-open-mode',
            {
                'default': False,
                'type': 'string',
                'metavar': '<os-open-mode>',
                'help': 'Integer or comma-separated list of integers (octal or decimal) of allowed modes. If set to a '
                'truthful value (ie. >0 or non-empty list), this checker will prefer `os.open` over the builtin `open`',
            },
        ),
    )
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
            'Avoid using `shell=True` when calling `subprocess` functions and avoid functions that internally call it',
            'avoid-shell-true',
            ' '.join(
                [
                    'Use of `shell=True` in subprocess functions or use of functions that internally set it should be'
                    'should be avoided',
                ]
            ),
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
        'E8010': (
            'Avoid using `os.popen()`',
            'avoid-os-popen',
            'Use of `os.popen()` should be avoided, as it internally uses `subprocess.Popen` with `shell=True`',
        ),
        'E8011': (
            'Avoid using `shlex.quote()` on non-POSIX platforms',
            'avoid-shlex-quote-on-non-posix',
            'Use of `shlex.quote()` should be avoided on non-POSIX platforms (such as Windows)',
        ),
        'W8012': (
            W8012_DISPLAY_MSG,
            'os-open-unsafe-permissions',
            'Avoid using `os.open` with unsafe file permissions (by default 0 <= mode <= 0o755)',
        ),
        'E8013': (
            'Avoid using `pickle.load` and `pickle.loads`',
            'avoid-pickle-load',
            'Use of `pickle.load` and `pickle.loads` should be avoided in favour of safer file formats',
        ),
        'E8014': (
            'Avoid using `marshal.load` and `marshal.loads`',
            'avoid-marshal-load',
            'Use of `marshal.load` and `marshal.loads` should be avoided in favour of safer file formats',
        ),
        'E8015': (
            'Avoid using `shelve.open()`',
            'avoid-shelve-open',
            'Use of `shelve.open()` should be avoided in favour of safer file formats',
        ),
    }

    def __init__(self, *args, **kwargs):
        """Initialize a SecureCodingStandardChecker object."""
        super().__init__(*args, **kwargs)
        self._prefer_os_open = False
        self._os_open_modes_allowed = []

    def visit_call(self, node):  # pylint: disable=too-many-branches
        """Visitor method called for astroid.Call nodes."""
        if _is_pdb_call(node):
            self.add_message('avoid-debug-stmt', node=node)
        elif _is_mktemp_call(node):
            self.add_message('replace-mktemp', node=node)
        elif _is_yaml_unsafe_call(node):
            self.add_message('avoid-yaml-unsafe-load', node=node)
        elif _is_function_call(node, module='jsonpickle', function='decode'):
            self.add_message('avoid-jsonpickle-decode', node=node)
        elif _is_function_call(node, module='os', function='system'):
            self.add_message('avoid-os-system', node=node)
        elif _is_os_path_call(node):
            self.add_message('replace-os-relpath-abspath', node=node)
        elif _is_shell_true_call(node):
            self.add_message('avoid-shell-true', node=node)
        elif _is_function_call(node, module='os', function='popen'):
            self.add_message('avoid-os-popen', node=node)
        elif _is_builtin_open_for_writing(node) and self._prefer_os_open:
            self.add_message('replace-builtin-open', node=node)
        elif isinstance(node.func, astroid.Name) and (node.func.name in ('eval', 'exec')):
            self.add_message('avoid-eval-exec', node=node)
        elif not _is_posix() and _is_function_call(node, module='shlex', function='quote'):
            self.add_message('avoid-shlex-quote-on-non-posix', node=node)
        elif (
            _is_function_call(node, module='os', function='open')
            and self._prefer_os_open
            and not _is_os_open_allowed_mode(node, self._os_open_modes_allowed)
        ):
            self.add_message('os-open-unsafe-permissions', node=node)
        elif _is_function_call(node, module='pickle', function=('load', 'loads')):
            self.add_message('avoid-pickle-load', node=node)
        elif _is_function_call(node, module='marshal', function=('load', 'loads')):
            self.add_message('avoid-marshal-load', node=node)
        elif _is_function_call(node, module='shelve', function='open'):
            self.add_message('avoid-shelve-open', node=node)

    def visit_import(self, node):
        """Visitor method called for astroid.Import nodes."""
        for (name, _) in node.names:
            if name == 'pdb':
                # Cover:
                #  * import pdb
                #  * import pdb as xxx
                self.add_message('avoid-debug-stmt', node=node)

    def visit_importfrom(self, node):
        """Visitor method called for astroid.ImportFrom nodes."""
        if node.modname == 'pdb':
            self.add_message('avoid-debug-stmt', node=node)
        elif node.modname == 'tempfile' and [name for (name, _) in node.names if name == 'mktemp']:
            self.add_message('replace-mktemp', node=node)
        elif node.modname in ('os.path', 'op') and [name for (name, _) in node.names if name in ('relpath', 'abspath')]:
            self.add_message('replace-os-relpath-abspath', node=node)
        elif (
            node.modname == 'subprocess'
            and [name for (name, _) in node.names if name in ('getoutput', 'getstatusoutput')]
        ) or ((node.modname == 'asyncio' and [name for (name, _) in node.names if name == 'create_subprocess_shell'])):
            self.add_message('avoid-shell-true', node=node)
        elif node.modname == 'os' and [name for (name, _) in node.names if name == 'system']:
            self.add_message('avoid-os-system', node=node)
        elif node.modname == 'os' and [name for (name, _) in node.names if name == 'popen']:
            self.add_message('avoid-os-popen', node=node)
        elif not _is_posix() and node.modname == 'shlex' and [name for (name, _) in node.names if name == 'quote']:
            self.add_message('avoid-shlex-quote-on-non-posix', node=node)
        elif node.modname == 'pickle' and [name for (name, _) in node.names if name in ('load', 'loads')]:
            self.add_message('avoid-pickle-load', node=node)
        elif node.modname == 'marshal' and [name for (name, _) in node.names if name in ('load', 'loads')]:
            self.add_message('avoid-marshal-load', node=node)
        elif node.modname == 'shelve' and [name for (name, _) in node.names if name == 'open']:
            self.add_message('avoid-shelve-open', node=node)

    def visit_with(self, node):
        """Visitor method called for astroid.With nodes."""
        for item in node.items:
            if item and isinstance(item[0], astroid.Call):
                if self._prefer_os_open:
                    if _is_builtin_open_for_writing(item[0]):
                        self.add_message('replace-builtin-open', node=node)
                    elif _is_function_call(item[0], module='os', function='open') and not _is_os_open_allowed_mode(
                        item[0], self._os_open_modes_allowed
                    ):
                        self.add_message('os-open-unsafe-permissions', node=node)
                elif _is_function_call(item[0], module='shelve', function='open'):
                    self.add_message('avoid-shelve-open', node=node)

    def visit_assert(self, node):
        """Visitor method called for astroid.Assert nodes."""
        self.add_message('avoid-assert', node=node)

    def set_os_open_mode(self, arg):
        """
        Control whether we prefer `os.open` over the builtin `open`.

        Args:
            arg (str): String with with mode value. Can be either of:
                - 'yes', 'y', 'true' (case-insensitive)
                    The maximum mode value is then set to self.DEFAULT_MAX_MODE
                - a single octal or decimal integer
                    The maximum mode value is then set to that integer value
                - a comma-separated list of integers (octal or decimal)
                    The allowed mode values are then those found in the list
                - anything else will disable the feature
        """

        def _str_to_int(arg):
            try:
                return int(arg, 8)
            except ValueError:
                return int(arg)

        def _update_display_msg(suffix=''):
            self.msg['W8012'] = (self.W8012_DISPLAY_MSG + suffix, self.msg['W8012'][1], self.msg['W8012'][2])

        arg = arg.lower()
        modes = [mode.strip() for mode in arg.split(',')]

        if len(modes) > 1:
            # Lists of allowed modes
            try:
                self._os_open_modes_allowed = [_str_to_int(mode) for mode in modes if mode]
                if not self._os_open_modes_allowed:
                    raise ValueError('Calculated empty value for `os_open_mode`!')
                self._prefer_os_open = True
                _update_display_msg(suffix=f' (mode in {modes})')
            except ValueError as error:
                raise ValueError(f'Unable to convert {modes} elements to integers!') from error
        elif modes and modes[0]:
            # Single values (ie. max allowed value for mode)
            try:
                val = _str_to_int(arg)
                self._prefer_os_open = val > 0
                if self._prefer_os_open:
                    self._os_open_modes_allowed = list(range(0, val + 1))
                    _update_display_msg(suffix=f' (mode <= {arg})')
                else:
                    self._os_open_modes_allowed.clear()
            except ValueError as error:
                if arg in ('y', 'yes', 'true'):
                    self._prefer_os_open = True
                    self._os_open_modes_allowed = list(range(0, self.DEFAULT_MAX_MODE + 1))
                    _update_display_msg(suffix=f' (mode <= {oct(self.DEFAULT_MAX_MODE)})')
                elif arg in ('n', 'no', 'false'):
                    self._prefer_os_open = False
                    self._os_open_modes_allowed.clear()
                else:
                    raise ValueError(f'Invalid value for `os_open_mode`: {arg}!') from error
        else:
            raise ValueError(f'Invalid value for `os_open_mode`: {arg}!')


def register(linter):  # pragma: no cover
    """Register the plugin to Pylint."""
    linter.register_checker(SecureCodingStandardChecker(linter))


def load_configuration(linter):  # pragma: no cover
    """Load data from the configuration file."""
    for checker in linter.get_checkers():
        if isinstance(checker, SecureCodingStandardChecker):
            checker.set_os_open_mode(checker.config.os_open_mode)
            break
