# Copyright (c) 2012 OpenStack Foundation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from neutron_lib import constants
from neutron_lib.plugins import directory
from oslo_config import cfg
from oslo_service import wsgi as base_wsgi
import routes as routes_mapper
import six.moves.urllib.parse as urlparse
import webob
import webob.dec
import webob.exc

from neutron.api import extensions
from neutron.api.v2 import attributes
from neutron.api.v2 import base
from neutron import manager
from neutron.pecan_wsgi import app as pecan_app
from neutron import policy
from neutron.quota import resource_registry
from neutron import wsgi


RESOURCES = attributes.CORE_RESOURCES
SUB_RESOURCES = {}
COLLECTION_ACTIONS = ['index', 'create']
MEMBER_ACTIONS = ['show', 'update', 'delete']
REQUIREMENTS = {'id': constants.UUID_PATTERN, 'format': 'json'}


class Index(wsgi.Application):
    def __init__(self, resources):
        self.resources = resources

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req):
        metadata = {}

        layout = []
        for name, collection in self.resources.items():
            href = urlparse.urljoin(req.path_url, collection)
            resource = {'name': name,
                        'collection': collection,
                        'links': [{'rel': 'self',
                                   'href': href}]}
            layout.append(resource)
        response = dict(resources=layout)
        content_type = req.best_match_content_type()
        body = wsgi.Serializer(metadata=metadata).serialize(response,
                                                            content_type)
        return webob.Response(body=body, content_type=content_type)


# 这个WSGI Application的具体功能就是实现模块功能的扩展和加载过程
# APIRouter在构造时，会根据配置文件core_plugin的配置加载plugin、extension管理器
class APIRouter(base_wsgi.Router):

    # 一个工厂方法
    @classmethod
    def factory(cls, global_config, **local_config):
        if cfg.CONF.web_framework == 'pecan':
            return pecan_app.v2_factory(global_config, **local_config)
        return cls(**local_config)

    # 真正调用的实例化方法
    def __init__(self, **local_config):
        mapper = routes_mapper.Mapper()
        manager.init()
        # 获取NeutronManager的core_plugin,在配置文件/etc/neutron/neutron.conf
        # core_plugin =  ml2
        plugin = directory.get_plugin()
        # 扫描特定路径下的extensions
        ext_mgr = extensions.PluginAwareExtensionManager.get_instance()
        ext_mgr.extend_resources("2.0", attributes.RESOURCE_ATTRIBUTE_MAP)

        col_kwargs = dict(collection_actions=COLLECTION_ACTIONS,
                          member_actions=MEMBER_ACTIONS)

        # 定义局部方法
        def _map_resource(collection, resource, params, parent=None):
            allow_bulk = cfg.CONF.allow_bulk
            controller = base.create_resource(
                collection, resource, plugin, params, allow_bulk=allow_bulk,
                parent=parent, allow_pagination=True,
                allow_sorting=True)
            path_prefix = None
            if parent:
                path_prefix = "/%s/{%s_id}/%s" % (parent['collection_name'],
                                                  parent['member_name'],
                                                  collection)
            mapper_kwargs = dict(controller=controller,
                                 requirements=REQUIREMENTS,
                                 path_prefix=path_prefix,
                                 **col_kwargs)
            # 将这些resource加入到router中
            return mapper.collection(collection, resource,
                                     **mapper_kwargs)

        mapper.connect('index', '/', controller=Index(RESOURCES))
        # 遍历 {'network': 'networks', 'subnet': 'subnets','port': 'ports'}
        # 添加controller
        # 对所有资源依次调用_map_resource()，完成资源的注册，并且完成资源与controller对应关系的建立
        for resource in RESOURCES:
            _map_resource(RESOURCES[resource], resource,
                          attributes.RESOURCE_ATTRIBUTE_MAP.get(
                              RESOURCES[resource], dict()))
            resource_registry.register_resource_by_name(resource)

        for resource in SUB_RESOURCES:
            _map_resource(SUB_RESOURCES[resource]['collection_name'], resource,
                          attributes.RESOURCE_ATTRIBUTE_MAP.get(
                              SUB_RESOURCES[resource]['collection_name'],
                              dict()),
                          SUB_RESOURCES[resource]['parent'])

        # Certain policy checks require that the extensions are loaded
        # and the RESOURCE_ATTRIBUTE_MAP populated before they can be
        # properly initialized. This can only be claimed with certainty
        # once this point in the code has been reached. In the event
        # that the policies have been initialized before this point,
        # calling reset will cause the next policy check to
        # re-initialize with all of the required data in place.
        policy.reset()
        super(APIRouter, self).__init__(mapper)
