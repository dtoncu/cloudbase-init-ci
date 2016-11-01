# Copyright 2016 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# pylint: disable=no-value-for-parameter, protected-access
# pylint: disable=no-name-in-module, too-many-public-methods

import time
import unittest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from argus.action_manager import windows as action_manager
from argus.client import windows as windows_client
from argus import exceptions
from argus.unit_tests import test_utils
from argus import util


class WinRemoteClientTest(unittest.TestCase):
    """Tests for WinRemoteClient class."""

    def setUp(self):
        self._cert_pem = mock.sentinel.cert_pem
        self._cert_key = mock.sentinel.cert_key

        action_manager.get_windows_action_manager = mock.Mock(
            return_value=mock.MagicMock())

        self._client = windows_client.WinRemoteClient(
            hostname=test_utils.HOSTNAME,
            username=test_utils.USERNAME,
            password=test_utils.PASSWORD,
            cert_pem=self._cert_pem,
            cert_key=self._cert_key)

    def _test_run_command(self, run_command_exc=None, get_cmd_output_exc=None,
                          exit_code=0):
        get_command = (lambda command, command_type=None:
                       "decorated-command[{} {}]".format(
                           command, command_type))
        util.get_command = mock.Mock(side_effect=get_command)

        protocol_client = mock.MagicMock()

        if run_command_exc:
            protocol_client.run_command.side_effect = run_command_exc
            with self.assertRaises(run_command_exc):
                self._client._run_command(
                    protocol_client, test_utils.SHELL_ID, test_utils.COMMAND)

            protocol_client.cleanup_command.assert_called_once_with(
                test_utils.SHELL_ID, None)

            return

        protocol_client.run_command.side_effect = test_utils.COMMAND_ID

        if get_cmd_output_exc:
            protocol_client.get_command_output.side_effect = get_cmd_output_exc
            with self.assertRaises(get_cmd_output_exc):
                self._client._run_command(
                    protocol_client, test_utils.SHELL_ID, test_utils.COMMAND)

            protocol_client.cleanup_command.assert_called_once_with(
                test_utils.SHELL_ID, test_utils.COMMAND_ID)

            return

        protocol_client.get_command_output.side_effect = [
            (test_utils.STDOUT, test_utils.STDERR, exit_code)
        ]

        if exit_code:
            with self.assertRaises(exceptions.ArgusError):
                self._client._run_command(
                    protocol_client, test_utils.SHELL_ID, test_utils.COMMAND)

            protocol_client.cleanup_command.assert_called_once_with(
                test_utils.SHELL_ID, test_utils.COMMAND_ID)

            return

        self.assertEqual(
            self._client._run_command(
                protocol_client, test_utils.SHELL_ID, test_utils.COMMAND,
                util.POWERSHELL),
            (test_utils.STDOUT, test_utils.STDERR, exit_code)
        )

        protocol_client.run_command.assert_called_once_with(
            test_utils.SHELL_ID, get_command(
                test_utils.COMMAND, util.POWERSHELL))

        protocol_client.get_command_output.assert_called_once_with(
            test_utils.SHELL_ID, test_utils.COMMAND_ID)

        protocol_client.cleanup_command.assert_called_once_with(
            test_utils.SHELL_ID, test_utils.COMMAND_ID)
