# Copyright 2011 OpenStack Foundation.
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

import abc

import six

from neutron_lib._i18n import _
from neutron_lib import constants


_UNSET = constants.Sentinel()


def is_extension_supported(plugin, alias):
    """Validate that the extension is supported.

    :param plugin: The plugin class.
    :param alias: The alias to check.
    :returns: True if the alias is supported else False.
    """
    return alias in getattr(plugin, "supported_extension_aliases", [])


@six.add_metaclass(abc.ABCMeta)
class ExtensionDescriptor(object):
    """Base class that defines the contract for extensions."""

    @abc.abstractmethod
    def get_name(self):
        """The name of the extension.

        e.g. 'Fox In Socks'
        """

    @abc.abstractmethod
    def get_alias(self):
        """The alias for the extension.

        e.g. 'FOXNSOX'
        """

    @abc.abstractmethod
    def get_description(self):
        """Friendly description for the extension.

        e.g. 'The Fox In Socks Extension'
        """

    @abc.abstractmethod
    def get_updated(self):
        """The timestamp when the extension was last updated.

        e.g. '2011-01-22T13:25:27-06:00'
        """
        # NOTE(justinsb): Not sure of the purpose of this is, vs the XML NS

    def get_resources(self):
        """List of extensions.ResourceExtension extension objects.

        Resources define new nouns, and are accessible through URLs.
        """
        return []

    def get_actions(self):
        """List of extensions.ActionExtension extension objects.

        Actions are verbs callable from the API.
        """
        return []

    def get_request_extensions(self):
        """List of extensions.RequestExtension extension objects.

        Request extensions are used to handle custom request data.
        """
        return []

    def get_extended_resources(self, version):
        """Retrieve extended resources or attributes for core resources.

        Extended attributes are implemented by a core plugin similarly
        to the attributes defined in the core, and can appear in
        request and response messages. Their names are scoped with the
        extension's prefix. The core API version is passed to this
        function, which must return a
        map[<resource_name>][<attribute_name>][<attribute_property>]
        specifying the extended resource attribute properties required
        by that API version.
        Extension can add resources and their attr definitions too.
        The returned map can be integrated into RESOURCE_ATTRIBUTE_MAP.
        """
        return {}

    def get_plugin_interface(self):
        """Returns an abstract class which defines contract for the plugin.

        The abstract class should inherit from
        neutron_lib.services.base.ServicePluginBase.
        Methods in this abstract class should be decorated as abstractmethod
        """

    def get_required_extensions(self):
        """Return list of extensions required for processing this descriptor.

        Without these extensions present in a neutron deployment, the
        introduced extension cannot load or function properly.
        """
        return []

    def get_optional_extensions(self):
        """Returns a list of optionally required extensions.

        Unlike get_required_extensions. This will not fail the loading of
        the extension if one of these extensions is not present. This is
        useful for an extension that extends multiple resources across
        other extensions that should still work for the remaining extensions
        when one is missing.
        """
        return []

    def update_attributes_map(self, extended_attributes,
                              extension_attrs_map=None):
        """Update attributes map for this extension.

        This is default method for extending an extension's attributes map.
        An extension can use this method and supplying its own resource
        attribute map in extension_attrs_map argument to extend all its
        attributes that needs to be extended.
        If an extension does not implement update_attributes_map, the method
        does nothing and just return.
        """
        if not extension_attrs_map:
            return

        for resource, attrs in extension_attrs_map.items():
            extended_attrs = extended_attributes.get(resource)
            if extended_attrs:
                attrs.update(extended_attrs)

    def get_pecan_resources(self):
        """List of PecanResourceExtension extension objects.

        Resources define new nouns, and are accessible through URLs.
        The controllers associated with each instance of
        extensions.ResourceExtension should be a subclass of
        neutron.pecan_wsgi.controllers.utils.NeutronPecanController.
        If a resource is defined in both get_resources and get_pecan_resources,
        the resource defined in get_pecan_resources will take precedence.
        """
        return []

# 基类neutron_lib.api.extensions.APIExtensionDescriptor,用来实现get_extended_resources()
class APIExtensionDescriptor(ExtensionDescriptor):
    """Base class that defines the contract for extensions.

    Concrete implementations of API extensions should first provide
    an API definition in neutron_lib.api.definitions. The API
    definition module (object reference) can then be specified as a
    class level attribute on the concrete extension.

    For example::

        from neutron_lib.api.definitions import provider_net
        from neutron_lib.api import extensions


        class Providernet(extensions.APIExtensionDescriptor):
            api_definition = provider_net
            # nothing else needed if default behavior is acceptable


    If extension implementations need to override the default behavior of
    this class they can override the respective method directly.
    """
    api_definition = _UNSET

    @classmethod
    def _assert_api_definition(cls, attr=None):
        if cls.api_definition == _UNSET:
            raise NotImplementedError(
                _("Extension module API definition not set."))
        if attr and getattr(cls.api_definition, attr, _UNSET) == _UNSET:
            raise NotImplementedError(_("Extension module API definition "
                                        "does not define '%s'") % attr)

    @classmethod
    def get_name(cls):
        """The name of the API definition."""
        cls._assert_api_definition('NAME')
        return cls.api_definition.NAME

    @classmethod
    def get_alias(cls):
        """The alias for the API definition."""
        cls._assert_api_definition('ALIAS')
        return cls.api_definition.ALIAS

    @classmethod
    def get_description(cls):
        """Friendly description for the API definition."""
        cls._assert_api_definition('DESCRIPTION')
        return cls.api_definition.DESCRIPTION

    @classmethod
    def get_updated(cls):
        """The timestamp when the API definition was last updated."""
        cls._assert_api_definition('UPDATED_TIMESTAMP')
        return cls.api_definition.UPDATED_TIMESTAMP

    def get_extended_resources(self, version):
        """Retrieve the resource attribute map for the API definition."""
        if version == "2.0":
            self._assert_api_definition('RESOURCE_ATTRIBUTE_MAP')
            return self.api_definition.RESOURCE_ATTRIBUTE_MAP
        else:
            return {}

    def get_required_extensions(self):
        """Returns the API definition's required extensions."""
        self._assert_api_definition('REQUIRED_EXTENSIONS')
        return self.api_definition.REQUIRED_EXTENSIONS

    def get_optional_extensions(self):
        """Returns the API definition's optional extensions."""
        self._assert_api_definition('OPTIONAL_EXTENSIONS')
        return self.api_definition.OPTIONAL_EXTENSIONS

    def update_attributes_map(self, attributes, extension_attrs_map=None):
        """Update attributes map for this extension.

        Behaves like ExtensionDescriptor.update_attributes_map(), but
        if extension_attrs_map is not given the extension's API
        definition RESOURCE_ATTRIBUTE_MAP is used.
        """
        if extension_attrs_map is None:
            extension_attrs_map = self.get_extended_resources('2.0')
        super(APIExtensionDescriptor, self).update_attributes_map(
            attributes, extension_attrs_map=extension_attrs_map)
