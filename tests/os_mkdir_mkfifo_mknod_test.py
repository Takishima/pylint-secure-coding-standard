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

import astroid
import pylint.testutils
import pytest

import pylint_secure_coding_standard as pylint_scs

_os_function_strings = {
    'mkdir': (
        'os.mkdir("/tmp/test", 0o777)',
        'os.mkdir(dir_name, 0o777)',
        'os.mkdir("/tmp/test", mode=0o777)',
        'os.mkdir(dir_name, mode=0o777)',
        'os.makedirs("/tmp/test/utils", 0o777)',
        'os.makedirs(dir_name, 0o777)',
        'os.makedirs("/tmp/test/utils", mode=0o777)',
        'os.makedirs(dir_name, mode=0o777)',
    ),
    'mkfifo': (
        'os.mkfifo("/tmp/test.log", 0o777)',
        'os.mkfifo(dir_name, 0o777)',
        'os.mkfifo("/tmp/test.log", mode=0o777)',
        'os.mkfifo(dir_name, mode=0o777)',
    ),
    'mknod': (
        'os.mknod("/tmp/test", 0o777)',
        'os.mknod(dir_name, 0o777)',
        'os.mknod("/tmp/test", mode=0o777)',
        'os.mknod(dir_name, mode=0o777)',
    ),
}


try:
    from pylint.testutils import MessageTest
except ImportError:
    from pylint.testutils import Message as MessageTest


class TestSecureCodingStandardChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = pylint_scs.SecureCodingStandardChecker

    @pytest.mark.parametrize('platform', ['Linux', 'Darwin', 'Java', 'Windows'])
    @pytest.mark.parametrize('function', ['mkdir', 'mkfifo', 'mknod'])
    @pytest.mark.parametrize('option', [False, True])
    @pytest.mark.parametrize(
        's',
        [
            # mkdir
            'os.mkdir("/tmp/test")',
            'os.mkdir(dir_name)',
            'os.mkdir("/tmp/test", 0o644)',
            'os.mkdir(dir_name, 0o644)',
            'os.mkdir("/tmp/test", mode=mode)',
            'os.mkdir(dir_name, mode=mode)',
            # makedirs
            'os.makedirs("/tmp/test/utils")',
            'os.makedirs(dir_name)',
            'os.makedirs("/tmp/test/utils", 0o644)',
            'os.makedirs(dir_name, 0o644)',
            'os.makedirs("/tmp/test/utils", mode=mode)',
            'os.makedirs(dir_name, mode=mode)',
            # mkfifo
            'os.mkfifo("/tmp/test/utils")',
            'os.mkfifo("/tmp/test/utils", 0o644)',
            'os.mkfifo("/tmp/test/utils", mode=mode)',
            # mknod
            'os.mknod(dir_name)',
            'os.mknod(dir_name, 0o644)',
            'os.mknod(dir_name, mode=mode)',
        ],
    )
    def test_os_function_ok(self, mocker, platform, function, option, s):
        mocker.patch('platform.system', return_value=platform)
        getattr(self.checker, f'set_os_{function}_allowed_modes')(str(option))

        node = astroid.extract_node(s + ' #@')

        with self.assertNoMessages():
            self.checker.visit_call(node)

    @pytest.mark.parametrize(
        ('platform', 'enabled_platform'),
        [
            ('Linux', True),
            ('Darwin', True),
            ('Java', False),
            ('Windows', False),
        ],
    )
    @pytest.mark.parametrize(
        'option',
        [False, True],
    )
    @pytest.mark.parametrize(
        ('function', 's'), [(function, s) for function, tests in _os_function_strings.items() for s in tests]
    )
    def test_os_function_call(self, mocker, platform, enabled_platform, function, option, s):
        mocker.patch('platform.system', return_value=platform)
        getattr(self.checker, f'set_os_{function}_allowed_modes')(str(option))

        print(s + ' #@')
        node = astroid.extract_node(s + ' #@')
        if enabled_platform and option:
            with self.assertAddsMessages(
                MessageTest(
                    msg_id=f'os-{function}-unsafe-permissions',
                    node=node,
                    args=(getattr(self.checker, f'_os_{function}_msg_arg'),),
                ),
                ignore_position=True,
            ):
                self.checker.visit_call(node)
        else:
            with self.assertNoMessages():
                self.checker.visit_call(node)
