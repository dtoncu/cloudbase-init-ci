# Copyright 2016 Cloudbase Solutions Srl
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

"""Config options available for the argus framework setup."""

from oslo_config import cfg

from argus.config import base as conf_base

_RESOURCES_LINK = ('https://raw.githubusercontent.com/cloudbase/'
                   'cloudbase-init-ci/master/argus/resources')


class ArgusOptions(conf_base.Options):

    """Config options available for the argus framework setup."""

    def __init__(self, config):
        super(ArgusOptions, self).__init__(config, group="argus")
        self._options = [
            cfg.StrOpt(
                "resources", default=_RESOURCES_LINK, required=True,
                help="An url that holds the resources usually from "
                     "/argus/resources available on the web"),
            cfg.BoolOpt("pause", default=False,
                        help="Pauses the CI after the installation process if "
                             "set on True."),
            cfg.ListOpt(
                "dns_nameservers", default=['8.8.8.8', '8.8.4.4'],
                help="A comma separated list of DNS IPs, which will be used "
                     "for network connectivity inside the instance."),
            cfg.StrOpt("output_directory", default=None,
                       help="The output directory path for where to save "
                            "instance details, if None is given, the current "
                            "working directory will be chosen."),
            cfg.StrOpt("build", default="Beta", required=True,
                       help="The build version type of the Cloudbase-init "
                            "installer that will be used."),
            cfg.StrOpt("arch", default="x64", required=True,
                       help="The architecture type that will be used for the "
                            "Cloudbase-init installer on the underlying "
                            "instance. A 'x64' option will be provided "
                            "for systems with an 64bit architecture, "
                            "and 'x86' for the 32bit systems."),
            cfg.StrOpt("patch_install", default=None,
                       help="Path to a link or file on the disk containing a "
                            "zip file with an updated version of "
                            "Cloudbase-init."),
            cfg.StrOpt("git_command", default=None,
                       help="Represents a git command that will be used to "
                            "checkout, clone or fetch a modified version of "
                            "Cloudbase-init, for replacing the present code "
                            "used by it."),
        ]

    def register(self):
        """Register the current options to the global ConfigOpts object."""
        group = cfg.OptGroup(self.group_name, title='Argus Options')
        self._config.register_group(group)
        self._config.register_opts(self._options, group=group)

    def list(self):
        """Return a list which contains all the available options."""
        return self._options
