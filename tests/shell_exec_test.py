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

    def test_shell_true_ok(self):
        nodes = astroid.extract_node(
            '''
            subprocess.Popen(["cat", "/etc/passwd"], b, e, i, o, e, pre, c) #@
            subprocess.Popen(["cat", "/etc/passwd"], b, e, i, o, e, pre, c, False) #@
            subprocess.Popen(["cat", "/etc/passwd"], b, e, i, o, e, pre, c, False, cwd) #@
            subprocess.Popen(["cat", "/etc/passwd"], shell=False) #@
            sp.Popen(["cat", "/etc/passwd"], shell=False) #@
            subprocess.run(["cat", "/etc/passwd"], shell=False) #@
            sp.run(["cat", "/etc/passwd"], shell=False) #@
            subprocess.call(["cat", "/etc/passwd"], shell=False) #@
            sp.call(["cat", "/etc/passwd"], shell=False) #@
            subprocess.check_call(["cat", "/etc/passwd"], shell=False) #@
            sp.check_call(["cat", "/etc/passwd"], shell=False) #@
            subprocess.check_output(["cat", "/etc/passwd"], shell=False) #@
            sp.check_output(["cat", "/etc/passwd"], shell=False) #@
            '''
        )

        with self.assertNoMessages():
            for node in nodes:
                self.checker.visit_call(node)

    @pytest.mark.parametrize(
        ('s', 'msg_id'),
        [
            ('from os import system', 'avoid-os-system'),
            ('from os import system as os_system', 'avoid-os-system'),
            ('from os import popen', 'avoid-os-popen'),
            ('from os import popen as os_popen', 'avoid-os-popen'),
            ('from subprocess import getoutput', 'avoid-shell-true'),
            ('from subprocess import getoutput as sp_getoutput', 'avoid-shell-true'),
            ('from subprocess import getstatusoutput', 'avoid-shell-true'),
            ('from subprocess import getstatusoutput as sp_getstatusoutput', 'avoid-shell-true'),
            ('from asyncio import create_subprocess_shell', 'avoid-shell-true'),
            ('from asyncio import create_subprocess_shell as create_sp_shell', 'avoid-shell-true'),
        ],
    )
    def test_shell_true_importfrom(self, s, msg_id):
        node = astroid.extract_node(s + ' #@')
        with self.assertAddsMessages(MessageTest(msg_id=msg_id, node=node), ignore_position=True):
            self.checker.visit_importfrom(node)

    @pytest.mark.parametrize(
        ('s', 'msg_id'),
        [
            ('os.system("ls -l")', 'avoid-os-system'),
            ('subprocess.Popen(["cat", "/etc/passwd"], b, e, i, o, e, pre, c, True)', 'avoid-shell-true'),
            ('subprocess.Popen(["cat", "/etc/passwd"], b, e, i, o, e, pre, c, True, cwd)', 'avoid-shell-true'),
            ('subprocess.run(["cat", "/etc/passwd"], shell=True)', 'avoid-shell-true'),
            ('sp.run(["cat", "/etc/passwd"], shell=True)', 'avoid-shell-true'),
            ('subprocess.call(["cat", "/etc/passwd"], shell=True)', 'avoid-shell-true'),
            ('sp.call(["cat", "/etc/passwd"], shell=True)', 'avoid-shell-true'),
            ('subprocess.check_call(["cat", "/etc/passwd"], shell=True)', 'avoid-shell-true'),
            ('sp.check_call(["cat", "/etc/passwd"], shell=True)', 'avoid-shell-true'),
            ('subprocess.check_output(["cat", "/etc/passwd"], shell=True)', 'avoid-shell-true'),
            ('sp.check_output(["cat", "/etc/passwd"], shell=True)', 'avoid-shell-true'),
            ('subprocess.getoutput("ls /bin/ls")', 'avoid-shell-true'),
            ('sp.getoutput("ls /bin/ls")', 'avoid-shell-true'),
            ('subprocess.getstatusoutput("ls /bin/ls")', 'avoid-shell-true'),
            ('sp.getstatusoutput("ls /bin/ls")', 'avoid-shell-true'),
            ('asyncio.create_subprocess_shell("ls /bin/ls")', 'avoid-shell-true'),
            ('asyncio.create_subprocess_shell(cmd)', 'avoid-shell-true'),
            ('asyncio.create_subprocess_shell("ls /bin/ls", stdin=PIPE, stdout=PIPE)', 'avoid-shell-true'),
            ('asyncio.create_subprocess_shell(cmd, stdin=PIPE, stdout=PIPE)', 'avoid-shell-true'),
            ('loop.subprocess_shell(asyncio.SubprocessProtocol, "ls /bin/ls")', 'avoid-shell-true'),
            ('loop.subprocess_shell(asyncio.SubprocessProtocol, cmd)', 'avoid-shell-true'),
            ('loop.subprocess_shell(asyncio.SubprocessProtocol, cmd, **kwds)', 'avoid-shell-true'),
            ('os.popen("cat")', 'avoid-os-popen'),
            ('os.popen("cat", "r")', 'avoid-os-popen'),
            ('os.popen("cat", "r", 1)', 'avoid-os-popen'),
            ('os.popen("cat", buffering=1)', 'avoid-os-popen'),
            ('os.popen("cat", mode="w")', 'avoid-os-popen'),
            ('os.popen("cat", mode="w", buffering=1)', 'avoid-os-popen'),
        ],
    )
    def test_shell_true_call(self, s, msg_id):
        node = astroid.extract_node(s + ' #@')
        with self.assertAddsMessages(MessageTest(msg_id=msg_id, node=node), ignore_position=True):
            self.checker.visit_call(node)
