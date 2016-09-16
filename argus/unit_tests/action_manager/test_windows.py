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

import unittest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from argus.action_manager import windows as action_manager
from argus import exceptions
from argus.introspection.cloud import windows as introspection
from argus import util


class WindowsActionManagerTest(unittest.TestCase):
    """Tests for windows action manager class."""

    def setUp(self):
        self._client = mock.MagicMock()
        self._config = mock.MagicMock()
        self._os_type = mock.sentinel

        self._action_manager = action_manager.WindowsActionManager(
            client=self._client, config=self._config, os_type=self._os_type)

    def _test_execute(self, exc=None):
        cmd = "fake-command"

        if exc:
            self._client.run_command_with_retry = mock.Mock(side_effect=exc)
            with self.assertRaises(exc):
                self._action_manager._execute(
                    cmd, count=util.RETRY_COUNT, delay=util.RETRY_DELAY,
                    command_type=util.CMD)
        else:
            self._client.run_command_with_retry = mock.Mock(
                return_value=("fake-stdout", "fake-stderr", 0))
            self.assertEqual(self._action_manager._execute(
                cmd, count=util.RETRY_COUNT, delay=util.RETRY_DELAY,
                command_type=util.CMD), "fake-stdout")
            self._client.run_command_with_retry.assert_called_once_with(
                cmd, count=util.RETRY_COUNT, delay=util.RETRY_DELAY,
                command_type=util.CMD)

    def test_execute(self):
        self._test_execute()

    def test_execute_argus_timeout_error(self):
        self._test_execute(exceptions.ArgusTimeoutError)

    def test_execute_argus_error(self):
        self._test_execute(exceptions.ArgusError)

    def _test_check_cbinit_installation(self, get_python_dir_exc=None,
                                        run_remote_cmd_exc=None):
        if get_python_dir_exc:
            introspection.get_python_dir = mock.Mock(
                side_effect=get_python_dir_exc)
            self.assertFalse(self._action_manager.check_cbinit_installation())
            return

        python_dir = r"fake\path"
        cmd = r'& "{}\python.exe" -c "import cloudbaseinit"'.format(python_dir)
        introspection.get_python_dir = mock.Mock(return_value=python_dir)
        if run_remote_cmd_exc:
            self._client.run_remote_cmd = mock.Mock(
                side_effect=run_remote_cmd_exc)
            self.assertFalse(self._action_manager.check_cbinit_installation())
            self._client.run_remote_cmd.assert_called_once_with(
                cmd=cmd, command_type=util.POWERSHELL)
            return

        self._client.run_remote_cmd = mock.Mock()
        self.assertTrue(self._action_manager.check_cbinit_installation())

    def test_check_cbinit_installation(self):
        self._test_check_cbinit_installation()

    def test_check_cbinit_installation_get_python_dir_exc(self):
        self._test_check_cbinit_installation(
            get_python_dir_exc=exceptions.ArgusError)

    def test_check_cbinit_installation_run_remote_cmd_exc(self):
        self._test_check_cbinit_installation(
            run_remote_cmd_exc=exceptions.ArgusError)

    @mock.patch('argus.action_manager.windows.WindowsActionManager.rmdir')
    def _test_cbinit_cleanup(self, mock_rmdir, get_cbinit_dir_exc=None,
                             rmdir_exc=None):
        if get_cbinit_dir_exc:
            introspection.get_cbinit_dir = mock.Mock(
                side_effect=get_cbinit_dir_exc)
            self.assertFalse(self._action_manager.cbinit_cleanup())
            return

        cbinit_dir = r"fake\path"
        introspection.get_cbinit_dir = mock.Mock(return_value=cbinit_dir)
        if rmdir_exc:
            mock_rmdir.side_effect = rmdir_exc
            self.assertFalse(self._action_manager.cbinit_cleanup())
            return

        self.assertTrue(self._action_manager.cbinit_cleanup())

    def test_cbinit_cleanup(self):
        self._test_cbinit_cleanup()

    def test_cbinit_cleanup_get_cbinit_dir_exc(self):
        self._test_cbinit_cleanup(get_cbinit_dir_exc=exceptions.ArgusError)

    def test_cbinit_cleanup_rmdir_exc(self):
        self._test_cbinit_cleanup(rmdir_exc=exceptions.ArgusError)

    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.cbinit_cleanup')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.check_cbinit_installation')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._deploy_using_scheduled_task')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._run_installation_script')
    def test_install_cbinit_run_installation_script(
            self, mock_run, mock_deploy, mock_check, mock_cleanup):
        mock_check.side_effect = [True]

        self.assertTrue(self._action_manager.install_cbinit())

        self.assertEqual(mock_run.call_count, 1)
        mock_deploy.assert_not_called()
        mock_cleanup.assert_not_called()

    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.cbinit_cleanup')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.check_cbinit_installation')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._deploy_using_scheduled_task')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._run_installation_script')
    def test_install_cbinit_deploy_using_scheduled_task(
            self, mock_run, mock_deploy, mock_check, mock_cleanup):
        mock_check.side_effect = [False, True]

        self.assertTrue(self._action_manager.install_cbinit())

        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(mock_deploy.call_count, 1)
        self.assertEqual(mock_cleanup.call_count, 1)

    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.cbinit_cleanup')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.check_cbinit_installation')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._deploy_using_scheduled_task')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._run_installation_script')
    def test_install_cbinit_run_installation_script_exc(
            self, mock_run, mock_deploy, mock_check, mock_cleanup):
        mock_check.side_effect = [False, True]
        mock_deploy.side_effect = exceptions.ArgusTimeoutError

        self.assertTrue(self._action_manager.install_cbinit())

        self.assertEqual(mock_run.call_count, 2)
        self.assertEqual(mock_deploy.call_count, 1)
        self.assertEqual(mock_cleanup.call_count, 2)

    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.cbinit_cleanup')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.check_cbinit_installation')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._deploy_using_scheduled_task')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._run_installation_script')
    def test_install_cbinit_at_last_try(
            self, mock_run, mock_deploy, mock_check, mock_cleanup):
        mock_check.side_effect = [True]

        run_fails = [
            exceptions.ArgusTimeoutError for _ in range(util.RETRY_COUNT)]
        deploy_fails = [
            exceptions.ArgusTimeoutError for _ in range(util.RETRY_COUNT - 1)]
        deploy_fails.append(None)

        mock_run.side_effect = run_fails
        mock_deploy.side_effect = deploy_fails

        self.assertTrue(self._action_manager.install_cbinit())

        self.assertEqual(mock_run.call_count, util.RETRY_COUNT)
        self.assertEqual(mock_deploy.call_count, util.RETRY_COUNT)
        self.assertEqual(mock_cleanup.call_count, util.RETRY_COUNT * 2 - 1)

    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.cbinit_cleanup')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.check_cbinit_installation')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._deploy_using_scheduled_task')
    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '._run_installation_script')
    def test_install_cbinit_timeout_fail(
            self, mock_run, mock_deploy, mock_check, mock_cleanup):
        mock_check.side_effect = [False for _ in range(2 * util.RETRY_COUNT)]

        self.assertFalse(self._action_manager.install_cbinit())

        self.assertEqual(mock_run.call_count, util.RETRY_COUNT)
        self.assertEqual(mock_deploy.call_count, util.RETRY_COUNT)
        self.assertEqual(mock_cleanup.call_count, 2 * util.RETRY_COUNT)

    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.execute_powershell_resource_script')
    def _test_run_installation_script(self, mock_execute_script, exc=None):
        installer = "fake_installer"

        if exc:
            mock_execute_script.side_effect = exc
            with self.assertRaises(exc):
                self._action_manager._run_installation_script(installer)
        else:
            self._action_manager._run_installation_script(installer)
            mock_execute_script.assert_called_once_with(
                resource_location='windows/installCBinit.ps1',
                parameters='-installer {}'.format(installer))

    def test_run_installation_script(self):
        self._test_run_installation_script()

    def test_run_installation_script_argus_timeout_error(self):
        self._test_run_installation_script(exc=exceptions.ArgusTimeoutError)

    def test_run_installation_script_argus_error(self):
        self._test_run_installation_script(exc=exceptions.ArgusError)

    @mock.patch('argus.action_manager.windows.WindowsActionManager'
                '.execute_cmd_resource_script')
    def _test_deploy_using_scheduled_task(self, mock_execute_script, exc=None):
        installer = "fake_installer"

        if exc:
            mock_execute_script.side_effect = exc
            with self.assertRaises(exc):
                self._action_manager._deploy_using_scheduled_task(installer)
        else:
            self._action_manager._deploy_using_scheduled_task(installer)
            mock_execute_script.assert_called_once_with(
                'windows/schedule_installer.bat',
                '-installer {}'.format(installer))

    def test_deploy_using_scheduled_task(self):
        self._test_deploy_using_scheduled_task()

    def test_deploy_using_scheduled_task_argus_timeout_error(self):
        self._test_deploy_using_scheduled_task(
            exc=exceptions.ArgusTimeoutError)

    def test_deploy_using_scheduled_task_argus_error(self):
        self._test_deploy_using_scheduled_task(exc=exceptions.ArgusError)
