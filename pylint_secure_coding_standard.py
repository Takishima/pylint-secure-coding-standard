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

from __future__ import annotations

import operator
import platform
import stat
from typing import ClassVar

import astroid
from pylint.checkers import BaseChecker

# ==============================================================================
# Helper functions


def _is_posix():
    """Return True if the current system is POSIX-compatible."""
    # NB: we could simply use `os.name` instead of `platform.system()`. However, that solution would be difficult to
    #     test using `mock` as a few modules (like `pytest`) actually use it internally...
    return platform.system() in ('Linux', 'Darwin')


_is_unix = _is_posix

# ==============================================================================


def _read_octal_mode_option(name, value, default):
    """
    Read an integer or list of integer configuration option.

    Args:
        name (str): Name of option
        value (str): Value of option from the configuration file or on the CLI. Its value can be any of:
            - 'yes', 'y', 'true' (case-insensitive)
                The maximum mode value is then set to self.DEFAULT_MAX_MODE
            - a single octal or decimal integer
                The maximum mode value is then set to that integer value
            - a comma-separated list of integers (octal or decimal)
                The allowed mode values are then those found in the list
            - anything else will count as a falseful value
        default (int,list): Default value for option if set to one of
            ('y', 'yes', 'true') in the configuration file or on the CLI

    Returns:
        A single integer or a (possibly empty) list of integers

    Raises:
        ValueError: if the value of the option is not valid
    """

    def _str_to_int(arg):
        try:
            return int(arg, 8)
        except ValueError:
            return int(arg)

    value = value.lower()
    modes = [mode.strip() for mode in value.split(',')]

    if len(modes) > 1:
        # Lists of allowed modes
        try:
            allowed_modes = [_str_to_int(mode) for mode in modes if mode]
        except ValueError as error:
            raise ValueError(f'Unable to convert {modes} elements to integers!') from error
        else:
            if not allowed_modes:
                raise ValueError(f'Calculated empty value for `{name}`!')
            return allowed_modes
    elif modes and modes[0]:
        # Single values (ie. max allowed value for mode)
        try:
            return _str_to_int(value)
        except ValueError as error:
            if value in ('y', 'yes', 'true'):
                return default
            if value in ('n', 'no', 'false'):
                return None
            raise ValueError(f'Invalid value for `{name}`: {value}!') from error
    else:
        raise ValueError(f'Invalid value for `{name}`: {value}!')


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
            #  * open(..., "w").
            #  * open(..., "wb").
            #  * open(..., "a").
            #  * open(..., "x").
            return True
    return False


def _get_mode_arg(node, args_idx):
    mode = None
    if len(node.args) > args_idx and isinstance(node.args[args_idx], astroid.Const):
        mode = node.args[args_idx].value
    elif node.keywords:
        for keyword in node.keywords:
            if keyword.arg == 'mode' and isinstance(keyword.value, astroid.Const):
                mode = keyword.value.value
                break
    return mode


def _is_allowed_mode(node, allowed_modes, args_idx):
    mode = _get_mode_arg(node, args_idx=args_idx)
    if mode is not None:
        return mode in allowed_modes

    # NB: default to True in all other cases
    return True


def _is_shell_true_call(node):
    _n_args_max = 8
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

            if (
                len(node.args) > _n_args_max
                and isinstance(node.args[_n_args_max], astroid.Const)
                and bool(node.args[_n_args_max].value)
            ):
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
    if (
        isinstance(node.func, astroid.Attribute)
        and isinstance(node.func.expr, astroid.Name)
        and node.func.expr.name == 'pdb'
    ):
        # Cover:
        return True
    if isinstance(node.func, astroid.Name) and node.func.name == 'Pdb':
        # Cover:
        return True
    return False


def _is_mktemp_call(node):
    if isinstance(node.func, astroid.Attribute) and node.func.attrname == 'mktemp':
        # Cover:
        #  * pdb.func().
        return True
    if isinstance(node.func, astroid.Name) and node.func.name == 'mktemp':
        # Cover:
        # * Pdb().
        return True
    return False


def _is_yaml_unsafe_call(node):
    _load_n_args_max = 2
    _safe_loaders = ('BaseLoader', 'SafeLoader')
    _unsafe_loaders = ('Loader', 'UnsafeLoader', 'FullLoader')

    if (
        isinstance(node.func, astroid.Attribute)
        and isinstance(node.func.expr, astroid.Name)
        and node.func.expr.name == 'yaml'
    ):
        if node.func.attrname in ('unsafe_load', 'full_load'):
            # Cover:
            #  * yaml.full_load().
            #  * yaml.unsafe_load().
            return True
        if node.func.attrname == 'load' and node.keywords:
            for keyword in node.keywords:
                if keyword.arg == 'Loader' and isinstance(keyword.value, astroid.Name):
                    if keyword.value.name in _unsafe_loaders:
                        # Cover:
                        #  * yaml.load(x, Loader=Loader).
                        #  * yaml.load(x, Loader=UnsafeLoader).
                        #  * yaml.load(x, Loader=FullLoader).
                        return True
                    if keyword.value.name in _safe_loaders:
                        # Cover:
                        #  * yaml.load(x, Loader=BaseLoader).
                        #  * yaml.load(x, Loader=SafeLoader).
                        return False
        elif node.func.attrname == 'load' and (
            len(node.args) < _load_n_args_max
            or (isinstance(node.args[1], astroid.Name) and node.args[1].name in _unsafe_loaders)
        ):
            # Cover:
            #  * yaml.load(x).
            #  * yaml.load(x, Loader).
            #  * yaml.load(x, UnsafeLoader).
            #  * yaml.load(x, FullLoader).
            return True

    if isinstance(node.func, astroid.Name) and node.func.name in ('unsafe_load', 'full_load'):
        # Cover:
        #  * unsafe_load(...).
        #  * full_load(...).
        return True
    return False


# ==============================================================================

_unop = {'-': operator.neg, 'not': operator.not_, '~': operator.inv}
_binop = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '//': operator.floordiv,
    '%': operator.mod,
    '^': operator.xor,
    '|': operator.or_,
    '&': operator.and_,
}
_chmod_known_mode_values = (
    'S_ISUID',
    'S_ISGID',
    'S_ENFMT',
    'S_ISVTX',
    'S_IREAD',
    'S_IWRITE',
    'S_IEXEC',
    'S_IRWXU',
    'S_IRUSR',
    'S_IWUSR',
    'S_IXUSR',
    'S_IRWXG',
    'S_IRGRP',
    'S_IWGRP',
    'S_IXGRP',
    'S_IRWXO',
    'S_IROTH',
    'S_IWOTH',
    'S_IXOTH',
)


def _chmod_get_mode(node):
    """
    Extract the mode constant of a node.

    Args:
        node (astroid.node_classes.NodeNG): an AST node

    Raises:
        ValueError: if a node is encountered that cannot be processed
    """
    if isinstance(node, astroid.Name) and node.name in _chmod_known_mode_values:
        return getattr(stat, node.name)
    if (
        isinstance(node, astroid.Attribute)
        and isinstance(node.expr, astroid.Name)
        and node.attrname in _chmod_known_mode_values
        and node.expr.name == 'stat'
    ):
        return getattr(stat, node.attrname)
    if isinstance(node, astroid.UnaryOp):
        return _unop[node.op](_chmod_get_mode(node.operand))
    if isinstance(node, astroid.BinOp):
        return _binop[node.op](_chmod_get_mode(node.left), _chmod_get_mode(node.right))

    raise ValueError(f'Do not know how to process node: {node.repr_tree()}')


def _chmod_has_wx_for_go(node):
    if platform.system() == 'Windows':
        # On Windows, only stat.S_IREAD and stat.S_IWRITE can be used, all other bits are ignored
        return False

    try:
        modes = None
        if len(node.args) > 1:
            modes = _chmod_get_mode(node.args[1])
        elif node.keywords:
            for keyword in node.keywords:
                if keyword.arg == 'mode':
                    modes = _chmod_get_mode(keyword.value)
                    break
    except ValueError:
        return False
    else:
        if modes is None:
            # NB: this would be from invalid code such as `os.chmod("file.txt")`
            raise RuntimeError('Unable to extract `mode` argument from function call!')
        # pylint: disable=no-member
        return bool(modes & (stat.S_IWGRP | stat.S_IXGRP | stat.S_IWOTH | stat.S_IXOTH))


# ==============================================================================


class SecureCodingStandardChecker(BaseChecker):  # pylint: disable=too-many-instance-attributes
    """Plugin class."""

    DEFAULT_MAX_MODE = 0o755

    name = 'secure-coding-standard'
    options = (
        (
            'os-open-mode',
            {
                'default': '0',
                'type': 'string',
                'metavar': '<os-open-mode>',
                'help': 'Integer or comma-separated list of integers (octal or decimal) of allowed modes. If set to a '
                'truthful value (ie. >0 or non-empty list), this checker will prefer `os.open` over the builtin `open`',
            },
        ),
        (
            'os-mkdir-mode',
            {
                'default': '0',
                'type': 'string',
                'metavar': '<os-mkdir-mode>',
                'help': 'Integer or comma-separated list of integers (octal or decimal) of allowed modes.',
            },
        ),
        (
            'os-mkfifo-mode',
            {
                'default': '0',
                'type': 'string',
                'metavar': '<os-mkfifo-mode>',
                'help': 'Integer or comma-separated list of integers (octal or decimal) of allowed modes.',
            },
        ),
        (
            'os-mknod-mode',
            {
                'default': '0',
                'type': 'string',
                'metavar': '<os-mknod-mode>',
                'help': 'Integer or comma-separated list of integers (octal or decimal) of allowed modes.',
            },
        ),
    )
    priority = -1

    msgs: ClassVar[dict[str, tuple[str, str, str]]] = {
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
        'E8002': ('Avoid using `os.system()`', 'avoid-os-system', 'Use of `os.system()` should be avoided'),
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
            'Use of debugging code should not be present in production code (e.g. `import pdb`)',
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
            'Avoid using `os.open` with unsafe permissions (should be %s)',
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
        'W8016': (
            'Avoid using `os.mkdir` and `os.makedirs` with unsafe permissions (should be %s)',
            'os-mkdir-unsafe-permissions',
            'Avoid using `os.mkdir` and `os.makedirs` with unsafe file permissions (by default 0 <= mode <= 0o755)',
        ),
        'W8017': (
            'Avoid using `os.mkfifo` with unsafe permissions (should be %s)',
            'os-mkfifo-unsafe-permissions',
            'Avoid using `os.mkfifo` with unsafe file permissions (by default 0 <= mode <= 0o755)',
        ),
        'W8018': (
            'Avoid using `os.mknod` with unsafe permissions (should be %s)',
            'os-mknod-unsafe-permissions',
            'Avoid using `os.mknod` with unsafe file permissions (by default 0 <= mode <= 0o755)',
        ),
        'W8019': (
            'Avoid using `os.chmod` with unsafe permissions (W ^ X for group and others)',
            'os-chmod-unsafe-permissions',
            'Avoid using `os.chmod` with unsafe file permissions (W ^ X for group and others)',
        ),
    }

    def __init__(self, linter):
        """Initialize a SecureCodingStandardChecker object."""
        super().__init__(linter)
        self._os_open_msg_arg = ''
        self._os_open_modes_allowed = []
        self._os_mkdir_msg_arg = ''
        self._os_mkdir_modes_allowed = []
        self._os_mkfifo_msg_arg = ''
        self._os_mkfifo_modes_allowed = []
        self._os_mknod_msg_arg = ''
        self._os_mknod_modes_allowed = []

    def visit_call(self, node):  # pylint: disable=too-many-branches # noqa: PLR0912
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
        elif _is_builtin_open_for_writing(node) and self._os_open_modes_allowed:
            self.add_message('replace-builtin-open', node=node)
        elif isinstance(node.func, astroid.Name) and (node.func.name in ('eval', 'exec')):
            self.add_message('avoid-eval-exec', node=node)
        elif not _is_posix() and _is_function_call(node, module='shlex', function='quote'):
            self.add_message('avoid-shlex-quote-on-non-posix', node=node)
        elif (
            _is_function_call(node, module='os', function='open')
            and self._os_open_modes_allowed
            and not _is_allowed_mode(node, self._os_open_modes_allowed, args_idx=2)
        ):
            self.add_message('os-open-unsafe-permissions', node=node, args=(self._os_open_msg_arg,))
        elif _is_function_call(node, module='pickle', function=('load', 'loads')):
            self.add_message('avoid-pickle-load', node=node)
        elif _is_function_call(node, module='marshal', function=('load', 'loads')):
            self.add_message('avoid-marshal-load', node=node)
        elif _is_function_call(node, module='shelve', function='open'):
            self.add_message('avoid-shelve-open', node=node)
        elif _is_function_call(node, module='os', function='chmod') and _chmod_has_wx_for_go(node):
            self.add_message('os-chmod-unsafe-permissions', node=node)
        elif _is_unix():
            if (
                _is_function_call(node, module='os', function=('mkdir', 'makedirs'))
                and self._os_mkdir_modes_allowed
                and not _is_allowed_mode(node, self._os_mkdir_modes_allowed, args_idx=1)
            ):
                self.add_message('os-mkdir-unsafe-permissions', node=node, args=(self._os_mkdir_msg_arg,))
            elif (
                _is_function_call(node, module='os', function='mkfifo')
                and self._os_mkfifo_modes_allowed
                and not _is_allowed_mode(node, self._os_mkfifo_modes_allowed, args_idx=1)
            ):
                self.add_message('os-mkfifo-unsafe-permissions', node=node, args=(self._os_mkfifo_msg_arg,))
            elif (
                _is_function_call(node, module='os', function='mknod')
                and self._os_mknod_modes_allowed
                and not _is_allowed_mode(node, self._os_mknod_modes_allowed, args_idx=1)
            ):
                self.add_message('os-mknod-unsafe-permissions', node=node, args=(self._os_mknod_msg_arg,))

    def visit_import(self, node):
        """Visitor method called for astroid.Import nodes."""
        for name, _ in node.names:
            if name == 'pdb':
                # Cover:
                #  * import pdb.
                #  * import pdb as xxx.
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
        ) or (node.modname == 'asyncio' and [name for (name, _) in node.names if name == 'create_subprocess_shell']):
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
                if self._os_open_modes_allowed:
                    if _is_builtin_open_for_writing(item[0]):
                        self.add_message('replace-builtin-open', node=node)
                    elif _is_function_call(item[0], module='os', function='open') and not _is_allowed_mode(
                        item[0], self._os_open_modes_allowed, args_idx=2
                    ):
                        self.add_message('os-open-unsafe-permissions', node=node)
                elif _is_function_call(item[0], module='shelve', function='open'):
                    self.add_message('avoid-shelve-open', node=node)

    def visit_assert(self, node):
        """Visitor method called for astroid.Assert nodes."""
        self.add_message('avoid-assert', node=node)

    def _set_mode_option(self, config_name, name, value):
        modes = _read_octal_mode_option(config_name, value, self.DEFAULT_MAX_MODE)

        if isinstance(modes, int) and modes > 0:
            setattr(self, f'_os_{name}_modes_allowed', list(range(modes + 1)))
            setattr(self, f'_os_{name}_msg_arg', f'0 < mode < {oct(modes)}')
        elif modes:
            setattr(self, f'_os_{name}_modes_allowed', modes)
            setattr(self, f'_os_{name}_msg_arg', f'mode in {[oct(mode) for mode in modes]}')
        else:
            getattr(self, f'_os_{name}_modes_allowed').clear()

    def set_os_open_allowed_modes(self, value):
        """
        Set the allowed modes for `os.open`.

        Note:
            This option has no effect on non-POSIX platforms.

        Args:
            value (str): Option value
        """
        self._set_mode_option('os_open_mode', 'open', value)

    def set_os_mkdir_allowed_modes(self, value):
        """
        Set the allowed modes for `os.mkdir` and `os.makedirs`.

        Note:
            This option has no effect on non-UNIX platforms.

        Args:
            value (str): Option value
        """
        self._set_mode_option('os_mkdir_mode', 'mkdir', value)

    def set_os_mkfifo_allowed_modes(self, value):
        """
        Set the allowed modes for `os.mkfifo`.

        Note:
            This option has no effect on non-UNIX platforms.

        Args:
            value (str): Option value
        """
        self._set_mode_option('os_mkfifo_mode', 'mkfifo', value)

    def set_os_mknod_allowed_modes(self, value):
        """
        Set the allowed modes for `os.mknod`.

        Note:
            This option has no effect on non-UNIX platforms.

        Args:
            value (str): Option value
        """
        self._set_mode_option('os_mknod_mode', 'mknod', value)


def register(linter):  # pragma: no cover
    """Register the plugin to Pylint."""
    linter.register_checker(SecureCodingStandardChecker(linter))


def load_configuration(linter):  # pragma: no cover
    """Load data from the configuration file."""
    for checker in linter.get_checkers():
        if isinstance(checker, SecureCodingStandardChecker):
            checker.set_os_open_allowed_modes(checker.config.os_open_mode)
            checker.set_os_mkdir_allowed_modes(checker.config.os_mkdir_mode)
            checker.set_os_mkfifo_allowed_modes(checker.config.os_mkfifo_mode)
            checker.set_os_mknod_allowed_modes(checker.config.os_mknod_mode)
