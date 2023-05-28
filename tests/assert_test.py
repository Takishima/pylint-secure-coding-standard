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

    def test_assert_ok(self):
        call_node1, call_node2 = astroid.extract_node(
            '''
        int(0) #@
        foo() #@
        '''
        )

        with self.assertNoMessages():
            self.checker.visit_call(call_node1)
            self.checker.visit_call(call_node2)

    @pytest.mark.parametrize(
        's',
        [
            'assert len(s) > 0',
            'assert (my_set and my_list), "Some message"',
        ],
    )
    def test_assert_not_ok(self, s):
        node = astroid.extract_node(s + ' #@')
        with self.assertAddsMessages(MessageTest(msg_id='avoid-assert', node=node), ignore_position=True):
            self.checker.visit_assert(node)
