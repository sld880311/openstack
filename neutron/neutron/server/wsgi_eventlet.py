#!/usr/bin/env python
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

import eventlet

from oslo_log import log

from neutron import service

LOG = log.getLogger(__name__)


def eventlet_wsgi_server():
    # 启动RESTful API 以协程方式
    # api服务的实现是NeutronApiService，这是一个符合WSGI规范的app，通过paste进行配置
    # neutron/service.py
    # paste文件位置可以在配置文件中指定，默认是/etc/neutron/api-paste.ini，在代码中是etc/api-paste.ini。
    # 查看api-paste.ini可以确定v2版api的实现是在neutron.api.v2.router:APIRouter
    neutron_api = service.serve_wsgi(service.NeutronApiService)
    # 启动RPC api
    start_api_and_rpc_workers(neutron_api)


def start_api_and_rpc_workers(neutron_api):
    try:
        worker_launcher = service.start_all_workers()

        pool = eventlet.GreenPool()
        api_thread = pool.spawn(neutron_api.wait)
        plugin_workers_thread = pool.spawn(worker_launcher.wait)

        # api and other workers should die together. When one dies,
        # kill the other.
        api_thread.link(lambda gt: plugin_workers_thread.kill())
        plugin_workers_thread.link(lambda gt: api_thread.kill())

        pool.waitall()
    except NotImplementedError:
        LOG.info("RPC was already started in parent process by "
                 "plugin.")

        neutron_api.wait()
