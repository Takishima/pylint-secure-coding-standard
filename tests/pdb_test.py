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

import astroid
import pytest

import pylint_secure_coding_standard as pylint_scs
import pylint.testutils


class TestSecureCodingStandardChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = pylint_scs.SecureCodingStandardChecker

    def test_pdb_ok(self):
        call_node1, call_node2 = astroid.extract_node(
            """
        int(0) #@
        foo() #@
        """
        )

        with self.assertNoMessages():
            self.checker.visit_call(call_node1)
            self.checker.visit_call(call_node2)

    @pytest.mark.parametrize(
        's',
        (
            'import pdb',
            'import pdb, six',
        ),
    )
    def test_pdb_import(self, s):
        node = astroid.extract_node(s + ' #@')
        with self.assertAddsMessages(pylint.testutils.Message(msg_id='avoid-debug-stmt', node=node)):
            self.checker.visit_import(node)

    @pytest.mark.parametrize(
        's',
        ('from pdb import set_trace',),
    )
    def test_pdb_importfrom(self, s):
        node = astroid.extract_node(s + ' #@')
        with self.assertAddsMessages(pylint.testutils.Message(msg_id='avoid-debug-stmt', node=node)):
            self.checker.visit_importfrom(node)

    @pytest.mark.parametrize(
        's',
        (
            'pdb.set_trace()',
            'pdb.post_mortem(traceback=None)',
            'pdb.Pdb(skip=["django.*"])',
            'Pdb(skip=["django.*"])',
        ),
    )
    def test_pdb_call(self, s):
        node = astroid.extract_node(s + ' #@')
        with self.assertAddsMessages(pylint.testutils.Message(msg_id='avoid-debug-stmt', node=node)):
            self.checker.visit_call(node)
