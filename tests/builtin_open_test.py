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

    def test_builtin_open_ok(self):
        nodes = astroid.extract_node(
            '''
            int(0) #@
            foo() #@
            open("file.txt") #@
            bla.open("file.txt") #@
            bla.open("file.txt", "w") #@
            with open("file.txt") as fd: fd.read() #@
            with bla.open("file.txt") as fd: fd.read() #@
            with bla.open("file.txt", "w") as fd: fd.read() #@
            '''
        )

        call_nodes = nodes[:5]
        with_nodes = nodes[5:]

        with self.assertNoMessages():
            self.checker.set_os_open_allowed_modes('True')
            for _idx, node in enumerate(call_nodes):
                self.checker.visit_call(node)
            for _idx, node in enumerate(with_nodes):
                self.checker.visit_with(node)

    _calls_not_ok = (
        'open("file.txt", "w")',
        'open("file.txt", "wb")',
        'open("file.txt", "bw")',
        'open("file.txt", "a")',
        'open("file.txt", "ab")',
        'open("file.txt", "ba")',
        'open("file.txt", "x")',
        'open("file.txt", "xb")',
        'open("file.txt", "bx")',
        'open("file.txt", mode)',
        'open("file.txt", mode="w")',
        'open("file.txt", mode="wb")',
        'open("file.txt", mode="bw")',
        'open("file.txt", mode="a")',
        'open("file.txt", mode="ab")',
        'open("file.txt", mode="ba")',
        'open("file.txt", mode="x")',
        'open("file.txt", mode="xb")',
        'open("file.txt", mode="bx")',
        'open("file.txt", mode=mode)',
    )

    @pytest.mark.parametrize('s', _calls_not_ok)
    @pytest.mark.parametrize('os_open_mode', [False, True])
    def test_builtin_open_call(self, s, os_open_mode):
        node = astroid.extract_node(s + ' #@')
        self.checker.set_os_open_allowed_modes(str(os_open_mode))
        if os_open_mode:
            with self.assertAddsMessages(MessageTest(msg_id='replace-builtin-open', node=node), ignore_position=True):
                self.checker.visit_call(node)
        else:
            with self.assertNoMessages():
                self.checker.visit_call(node)

    @pytest.mark.parametrize('s', ['with ' + s + ' as fd: fd.read()' for s in _calls_not_ok])
    @pytest.mark.parametrize('os_open_mode', [False, True])
    def test_builtin_open_with(self, s, os_open_mode):
        node = astroid.extract_node(s + ' #@')
        self.checker.set_os_open_allowed_modes(str(os_open_mode))
        if os_open_mode:
            with self.assertAddsMessages(MessageTest(msg_id='replace-builtin-open', node=node), ignore_position=True):
                self.checker.visit_with(node)
        else:
            with self.assertNoMessages():
                self.checker.visit_with(node)
