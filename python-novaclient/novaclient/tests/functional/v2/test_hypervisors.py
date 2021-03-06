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

from novaclient.tests.functional.v2.legacy import test_hypervisors


class TestHypervisorsV28(test_hypervisors.TestHypervisors):

    COMPUTE_API_VERSION = "2.28"

    def test_list(self):
        self._test_list(dict)


class TestHypervisorsV2_53(TestHypervisorsV28):
    COMPUTE_API_VERSION = "2.53"

    def test_list(self):
        self._test_list(cpu_info_type=dict, uuid_as_id=True)
