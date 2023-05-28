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
        'arg',
        ['True', '0o644', '0o644,'],
    )
    def test_os_open_ok(self, arg):
        nodes = astroid.extract_node(
            '''
            int(0) #@
            foo() #@
            os.open("file.txt") #@
            os.open("file.txt", flags, mode) #@
            os.open("file.txt", os.O_RDONLY) #@
            os.open("file.txt", os.O_RDONLY, mode) #@
            os.open("file.txt", os.O_RDONLY, 0o644) #@
            os.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW) #@
            os.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, mode) #@
            os.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, 0o644) #@
            os.open("file.txt", os.O_RDONLY, mode=mode) #@
            os.open("file.txt", os.O_RDONLY, mode=0o644) #@
            os.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, mode=mode) #@
            os.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, mode=0o644) #@
            bla.open("file.txt") #@
            bla.open("file.txt", os.O_RDONLY) #@
            bla.open("file.txt", flags=os.O_RDONLY) #@
            bla.open("file.txt", os.O_RDONLY, mode) #@
            bla.open("file.txt", os.O_RDONLY, 0o644) #@
            bla.open("file.txt", os.O_RDONLY, 0o777) #@
            bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW) #@
            bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, mode) #@
            bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, 0o644) #@
            bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, 0o777) #@
            bla.open("file.txt", os.O_RDONLY, mode=mode) #@
            bla.open("file.txt", os.O_RDONLY, mode=0o644) #@
            bla.open("file.txt", os.O_RDONLY, mode=0o777) #@
            bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW) #@
            bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, mode=mode) #@
            bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, mode=0o644) #@
            bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, mode=0o777) #@
            with os.open("file.txt") as fd: fd.read() #@
            with os.open("file.txt", flags, mode) as fd: fd.read() #@
            with os.open("file.txt", os.O_RDONLY) as fd: fd.read() #@
            with os.open("file.txt", os.O_RDONLY, mode) as fd: fd.read() #@
            with os.open("file.txt", os.O_RDONLY, 0o644) as fd: fd.read() #@
            with os.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW) as fd: fd.read() #@
            with os.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, mode) as fd: fd.read() #@
            with os.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, 0o644) as fd: fd.read() #@
            with os.open("file.txt", flags=flags, mode=mode) as fd: fd.read() #@
            with os.open("file.txt", flags=os.O_RDONLY, mode=mode) as fd: fd.read() #@
            with os.open("file.txt", flags=os.O_RDONLY, mode=0o644) as fd: fd.read() #@
            with os.open("file.txt", flags=os.O_RDONLY | os.O_NOFOLLOW, mode=mode) as fd: fd.read() #@
            with os.open("file.txt", flags=os.O_RDONLY | os.O_NOFOLLOW, mode=0o644) as fd: fd.read() #@
            with bla.open("file.txt") as fd: fd.read() #@
            with bla.open("file.txt", os.O_RDONLY) as fd: fd.read() #@
            with bla.open("file.txt", os.O_RDONLY, mode) as fd: fd.read() #@
            with bla.open("file.txt", os.O_RDONLY, 0o644) as fd: fd.read() #@
            with bla.open("file.txt", os.O_RDONLY, 0o777) as fd: fd.read() #@
            with bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW) as fd: fd.read() #@
            with bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, mode) as fd: fd.read() #@
            with bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, 0o644) as fd: fd.read() #@
            with bla.open("file.txt", os.O_RDONLY | os.O_NOFOLLOW, 0o777) as fd: fd.read() #@
            with bla.open("file.txt", flags=os.O_RDONLY) as fd: fd.read() #@
            with bla.open("file.txt", flags=os.O_RDONLY, mode=mode) as fd: fd.read() #@
            with bla.open("file.txt", flags=os.O_RDONLY, mode=0o644) as fd: fd.read() #@
            with bla.open("file.txt", flags=os.O_RDONLY, mode=0o777) as fd: fd.read() #@
            with bla.open("file.txt", flags=os.O_RDONLY | os.O_NOFOLLOW, mode=mode) as fd: fd.read() #@
            with bla.open("file.txt", flags=os.O_RDONLY | os.O_NOFOLLOW, mode=0o644) as fd: fd.read() #@
            with bla.open("file.txt", flags=os.O_RDONLY | os.O_NOFOLLOW, mode=0o777) as fd: fd.read() #@
            '''
        )

        self.checker.set_os_open_allowed_modes(arg)

        call_nodes = []
        with_nodes = []

        # Find index of first line starting with 'with'
        for node in nodes:
            if isinstance(node, astroid.With):
                with_nodes.append(node)
            else:
                call_nodes.append(node)

        with self.assertNoMessages():
            for _idx, node in enumerate(call_nodes):
                self.checker.visit_call(node)
            for _idx, node in enumerate(with_nodes):
                self.checker.visit_with(node)

    # ==========================================================================

    @pytest.mark.parametrize('mode', range(0o756, 0o777 + 1), ids=lambda arg: oct(arg))
    @pytest.mark.parametrize(
        ('arg', 'expected_warning'),
        [
            ('False', False),
            ('True', True),
        ],
    )
    def test_os_open_call_default_modes(self, mode, arg, expected_warning):
        code = f'os.open("file.txt", os.O_WRONLY, 0o{mode:o}) #@'
        print(code)
        node = astroid.extract_node(code)
        self.checker.set_os_open_allowed_modes(arg)
        if expected_warning:
            with self.assertAddsMessages(
                MessageTest(msg_id='os-open-unsafe-permissions', node=node, args=(self.checker._os_open_msg_arg,)),
                ignore_position=True,
            ):
                self.checker.visit_call(node)
        else:
            with self.assertNoMessages():
                self.checker.visit_call(node)

    # --------------------------------------------------------------------------

    @pytest.mark.parametrize('mode', range(0o750, 0o761), ids=lambda arg: oct(arg))
    @pytest.mark.parametrize(
        'call_mode',
        [
            'os.open("file.txt", os.O_WRONLY, 0o{:o}) #@',
            'os.open("file.txt", flags=os.O_WRONLY, mode=0o{:o}) #@',
        ],
        ids=('args', 'keyword'),
    )
    @pytest.mark.parametrize(
        ('arg', 'expected_warning'),
        [
            ('False', False),
            ('0o755,', True),
        ],
        ids=('False-False', '[0o755]-True'),
    )
    def test_os_open_call(self, mode, call_mode, arg, expected_warning):
        node = astroid.extract_node(call_mode.format(mode))
        self.checker.set_os_open_allowed_modes(arg)
        if expected_warning and mode != 0o755:
            with self.assertAddsMessages(
                MessageTest(msg_id='os-open-unsafe-permissions', node=node, args=(self.checker._os_open_msg_arg,)),
                ignore_position=True,
            ):
                self.checker.visit_call(node)
        else:
            with self.assertNoMessages():
                self.checker.visit_call(node)

    # ==========================================================================

    @pytest.mark.parametrize('mode', range(0o756, 0o777 + 1), ids=lambda arg: oct(arg))
    @pytest.mark.parametrize(
        'call_mode',
        [
            'with os.open("file.txt", os.O_WRONLY, 0o{:o}) as fd: fd.read() #@',
            'with os.open("file.txt", flags=os.O_WRONLY, mode=0o{:o}) as fd: fd.read() #@',
        ],
        ids=('args', 'keyword'),
    )
    @pytest.mark.parametrize(
        ('arg', 'expected_warning'),
        [
            ('False', False),
            ('True', True),
        ],
    )
    def test_os_open_with_default_modes(self, mode, call_mode, arg, expected_warning):
        node = astroid.extract_node(call_mode.format(mode))
        self.checker.set_os_open_allowed_modes(arg)
        if expected_warning:
            with self.assertAddsMessages(
                MessageTest(msg_id='os-open-unsafe-permissions', node=node), ignore_position=True
            ):
                self.checker.visit_with(node)
        else:
            with self.assertNoMessages():
                self.checker.visit_with(node)

    # --------------------------------------------------------------------------

    @pytest.mark.parametrize('mode', range(0o750, 0o761), ids=lambda arg: oct(arg))
    @pytest.mark.parametrize(
        ('arg', 'expected_warning'),
        [
            ('False', False),
            ('0o755,', True),
        ],
    )
    def test_os_open_with(self, mode, arg, expected_warning):
        node = astroid.extract_node(f'with os.open("file.txt", os.O_WRONLY, 0o{mode:o}) as fd: fd.read() #@')
        self.checker.set_os_open_allowed_modes(arg)
        if expected_warning and mode != 0o755:
            with self.assertAddsMessages(
                MessageTest(msg_id='os-open-unsafe-permissions', node=node), ignore_position=True
            ):
                self.checker.visit_with(node)
        else:
            with self.assertNoMessages():
                self.checker.visit_with(node)
