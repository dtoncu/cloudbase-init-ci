# Copyright 2015 Cloudbase Solutions Srl
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

import collections
import contextlib

from argus.scenarios import base
from argus.scenarios import service_mock


class named(collections.namedtuple("service", "application script_name "
                                              "host port")):

    @property
    def stop_link(self):
        link = "http://{host}:{port}{script_name}/stop_me/"
        return link.format(host=self.host,
                           port=self.port,
                           script_name=self.script_name)


class BaseServiceMockMixin(object):
    """Mixin class for mocking metadata services.

    In order to have support for mocked metadata services, set a list
    of :meth:`named` entries in the class, as such::

        class Test(BaseServiceMockMixin, BaseScenario):
            services = [
                 named(application, script_name, host, port)
            ]

    These services will be started and will be stopped after
    :meth:`prepare_instance` finishes.
    """

    @classmethod
    @contextlib.contextmanager
    def instantiate_mock_services(cls):
        with service_mock.instantiate_services(cls.services, cls.backend):
            yield

    @classmethod
    def prepare_instance(cls):
        with cls.instantiate_mock_services():
            super(BaseServiceMockMixin, cls).prepare_instance()


class EC2WindowsScenario(BaseServiceMockMixin, base.BaseScenario):
    """Scenario for testing the EC2 metadata service."""

    services = [
        named(application=service_mock.EC2MetadataServiceApp,
              script_name="/2009-04-04/meta-data",
              host="0.0.0.0",
              port=2000),
    ]


class CloudstackWindowsScenario(BaseServiceMockMixin,
                                base.BaseScenario):
    """Scenario for testing the Cloudstack metadata service."""

    services = [
        named(application=service_mock.CloudstackMetadataServiceApp,
              script_name="",
              host="0.0.0.0",
              port=2001),
        named(application=service_mock.CloudstackPasswordManagerApp,
              script_name="",
              host="0.0.0.0",
              port=8080),
    ]


class MaasWindowsScenario(BaseServiceMockMixin, base.BaseScenario):
    """Scenario for testing the Maas metadata service."""

    services = [
        named(application=service_mock.MaasMetadataServiceApp,
              script_name="/2012-03-01",
              host="0.0.0.0",
              port=2002),
    ]


class HTTPKeysWindowsScenario(BaseServiceMockMixin, base.BaseScenario):

    """Scenario for testing custom OpenStack http metadata service."""

    services = [
        named(application=service_mock.HTTPKeysMetadataServiceApp,
              script_name="/openstack",
              host="0.0.0.0",
              port=2003)
    ]
