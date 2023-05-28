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

try:
    from pylint.testutils import MessageTest
except ImportError:
    from pylint.testutils import Message as MessageTest


class TestSecureCodingStandardChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = pylint_scs.SecureCodingStandardChecker

    @pytest.mark.parametrize(
        ('platform', 'expected_success'),
        [
            ('Linux', True),
            ('Darwin', True),
            ('Java', False),
            ('Windows', False),
        ],
    )
    @pytest.mark.parametrize('s', ['from shlex import quote'])
    def test_shlex_quote_importfrom(self, mocker, platform, expected_success, s):
        mocker.patch('platform.system', return_value=platform)

        node = astroid.extract_node(s + ' #@')
        if expected_success:
            self.checker.visit_importfrom(node)
        else:
            with self.assertAddsMessages(
                MessageTest(msg_id='avoid-shlex-quote-on-non-posix', node=node), ignore_position=True
            ):
                self.checker.visit_importfrom(node)

    @pytest.mark.parametrize(
        ('platform', 'expected_success'),
        [
            ('Linux', True),
            ('Darwin', True),
            ('Java', False),
            ('Windows', False),
        ],
    )
    @pytest.mark.parametrize(
        's',
        [
            'shlex.quote("ls -l")',
            'shlex.quote(command_str)',
        ],
    )
    def test_shlex_call_quote(self, mocker, platform, expected_success, s):
        mocker.patch('platform.system', return_value=platform)

        node = astroid.extract_node(s + ' #@')
        if expected_success:
            self.checker.visit_call(node)
        else:
            with self.assertAddsMessages(
                MessageTest(msg_id='avoid-shlex-quote-on-non-posix', node=node), ignore_position=True
            ):
                self.checker.visit_call(node)
