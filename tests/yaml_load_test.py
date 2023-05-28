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

    def test_yaml_ok(self):
        nodes = astroid.extract_node(
            '''
            int(0) #@
            foo() #@
            yaml.safe_load("!!python/object/new:os.system [echo EXPLOIT!]") #@
            yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", Loader=BaseLoader) #@
            yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", Loader=SafeLoader) #@
            yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", BaseLoader) #@
            yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", SafeLoader) #@
            '''
        )

        with self.assertNoMessages():
            for node in nodes:
                print(node)
                self.checker.visit_call(node)

    @pytest.mark.parametrize(
        's',
        [
            'full_load("!!python/object/new:os.system [echo EXPLOIT!]")',
            'unsafe_load("!!python/object/new:os.system [echo EXPLOIT!]")',
            'yaml.load("!!python/object/new:os.system [echo EXPLOIT!]")',
            'yaml.full_load("!!python/object/new:os.system [echo EXPLOIT!]")',
            'yaml.unsafe_load("!!python/object/new:os.system [echo EXPLOIT!]")',
            'yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", Loader=Loader)',
            'yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", Loader=UnsafeLoader)',
            'yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", Loader=FullLoader)',
            'yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", Loader)',
            'yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", UnsafeLoader)',
            'yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", FullLoader)',
        ],
    )
    def test_yaml_not_ok(self, s):
        node = astroid.extract_node(s + ' #@')
        with self.assertAddsMessages(MessageTest(msg_id='avoid-yaml-unsafe-load', node=node), ignore_position=True):
            self.checker.visit_call(node)
