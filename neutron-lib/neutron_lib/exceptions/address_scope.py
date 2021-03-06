# All rights reserved.
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

from neutron_lib._i18n import _
from neutron_lib import exceptions


class AddressScopeNotFound(exceptions.NotFound):
    message = _("Address scope %(address_scope_id)s could not be found.")


class AddressScopeInUse(exceptions.InUse):
    message = _("Unable to complete operation on "
                "address scope %(address_scope_id)s. There are one or more "
                "subnet pools in use on the address scope.")


class AddressScopeUpdateError(exceptions.BadRequest):
    message = _("Unable to update address scope %(address_scope_id)s : "
                "%(reason)s.")
