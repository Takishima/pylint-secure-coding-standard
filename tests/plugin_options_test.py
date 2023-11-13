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

import pylint.testutils
import pytest

import pylint_secure_coding_standard as pylint_scs

_default_modes = list(range(pylint_scs.SecureCodingStandardChecker.DEFAULT_MAX_MODE + 1))


def _id_func(arg):
    _max_len = 4
    if arg == _default_modes:
        return 'default_modes'
    if isinstance(arg, list) and len(arg) > _max_len:
        return '[{}...{}]'.format(
            ','.join(str(val) for val in arg[:_max_len]),
            ','.join(str(val) for val in arg[-_max_len:]),
        )
    return str(arg)


class TestSecureCodingStandardChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = pylint_scs.SecureCodingStandardChecker

    @pytest.mark.parametrize(
        ('arg', 'expected'),
        [
            ('0', 0),
            ('false', None),
            ('False', None),
            ('n', None),
            ('no', None),
            ('No', None),
            ('NO', None),
            ('y', _default_modes),
            ('yes', _default_modes),
            ('Yes', _default_modes),
            ('YES', _default_modes),
            ('true', _default_modes),
            ('True', _default_modes),
            ('1', 1),
            ('493', 493),
            ('0o755', 0o755),
            ('0o755,', [0o755]),
            ('0o644, 0o755,', [0o644, 0o755]),
        ],
        ids=_id_func,
    )
    def test_read_octal_mode_option(self, arg, expected):
        print(f'INFO: expected: {expected}')
        assert pylint_scs._read_octal_mode_option('test', arg, _default_modes) == expected

    @pytest.mark.parametrize('arg', ['', ',', ',,', 'nope', 'asd', 'a,', '493, a'])
    def test_read_octal_mode_option_invalid(self, arg):
        # with pytest.raises(ValueError, match='^Unable to convert .* elements to integers!$'):
        with pytest.raises(ValueError, match='^(Invalid value for|Calculated empty value for|Unable to convert).*'):
            pylint_scs._read_octal_mode_option('test', arg, _default_modes)

    @pytest.mark.parametrize('function', ['open', 'mkdir', 'mkfifo', 'mknod'])
    @pytest.mark.parametrize(
        ('arg', 'allowed_modes'),
        [
            ('n', []),
            ('y', _default_modes),
            ('0', []),
            ('0o755', _default_modes),
            ('0o644, 0o755,', [0o644, 0o755]),
        ],
        ids=_id_func,
    )
    def test_os_allowed_mode(self, function, arg, allowed_modes):
        print(f'INFO: allowed_modes: {allowed_modes}')
        getattr(self.checker, f'set_os_{function}_allowed_modes')(arg)
        assert getattr(self.checker, f'_os_{function}_modes_allowed') == allowed_modes
