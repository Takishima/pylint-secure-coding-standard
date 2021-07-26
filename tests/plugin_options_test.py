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

import pylint.testutils
import pytest

import pylint_secure_coding_standard as pylint_scs

_default_modes = list(range(0, pylint_scs.SecureCodingStandardChecker.DEFAULT_MAX_MODE + 1))


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
        'arg, prefer_os_open, allowed_modes',
        (
            ('0', False, []),
            ('false', False, []),
            ('False', False, []),
            ('n', False, []),
            ('no', False, []),
            ('No', False, []),
            ('NO', False, []),
            ('y', True, _default_modes),
            ('yes', True, _default_modes),
            ('Yes', True, _default_modes),
            ('YES', True, _default_modes),
            ('true', True, _default_modes),
            ('True', True, _default_modes),
            ('1', True, [0, 1]),
            ('2', True, [0, 1, 2]),
            ('0o755', True, _default_modes),
            ('0o755,', True, [0o755]),
            ('0o644, 0o755,', True, [0o644, 0o755]),
            ('493', True, _default_modes),
            ('0o644', True, list(range(0, 0o644 + 1))),
        ),
        ids=_id_func,
    )
    def test_os_open_mode_option(self, arg, prefer_os_open, allowed_modes):
        print(f'INFO: allowed_modes: {allowed_modes}')
        self.checker.set_os_open_mode(arg)
        assert self.checker._prefer_os_open == prefer_os_open
        assert self.checker._os_open_modes_allowed == allowed_modes

    @pytest.mark.parametrize('arg', ('', ',', ',,', 'asd', 'a,', '493, a'))
    def test_os_open_mode_option_invalid(self, arg):
        with pytest.raises(ValueError):
            self.checker.set_os_open_mode(arg)
