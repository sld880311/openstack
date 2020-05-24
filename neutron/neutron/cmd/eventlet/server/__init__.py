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

from neutron import server
from neutron.server import rpc_eventlet
from neutron.server import wsgi_eventlet

#  Neutron-Server启动，无外乎就是加载配置，router各种resource，然后就等待请求了。
# 其中router哪些resource完全是由配置文件来决定的。
# 当然，在启动的过程中也会初始化db，这也就是为何在安装neutron的时候无需像nova，glance等要执行db sync的原因了。


# 创建API服务
def main():
    server.boot_server(wsgi_eventlet.eventlet_wsgi_server)


# 创建rpc服务
# 调用过程：根据配置文件中的core_plugin和service_plugins的配置加载plugin，创建对应的RpcWorker，开始监听rpc
# 通过调用plugin的start_rpc_listeners进行监听
def main_rpc_eventlet():
    server.boot_server(rpc_eventlet.eventlet_rpc_server)
