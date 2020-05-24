# Copyright (c) 2015 OpenStack Foundation.
#
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

import sys

from oslo_config import cfg
from oslo_service import service

from neutron.agent.linux import external_process
from neutron.agent.linux import interface
from neutron.agent.linux import pd
from neutron.agent.linux import ra
from neutron.common import config as common_config
from neutron.common import topics
from neutron.conf.agent import common as config
from neutron.conf.agent.l3 import config as l3_config
from neutron.conf.agent.l3 import ha as ha_conf
from neutron.conf.agent.metadata import config as meta_conf
from neutron import service as neutron_service


def register_opts(conf):
    l3_config.register_l3_agent_config_opts(l3_config.OPTS, conf)
    ha_conf.register_l3_agent_ha_opts(conf)
    meta_conf.register_meta_conf_opts(meta_conf.SHARED_OPTS, conf)
    config.register_interface_driver_opts_helper(conf)
    config.register_agent_state_opts_helper(conf)
    conf.register_opts(interface.OPTS)
    conf.register_opts(external_process.OPTS)
    conf.register_opts(pd.OPTS)
    conf.register_opts(ra.OPTS)
    config.register_availability_zone_opts_helper(conf)


# l3 agent使用Linux ip协议栈和iptables来实现router和NAT的功能
# 如果在horizon的界面创建一个路由，不进行任何操作的话，plugin只会操作数据库，l3 agent不会作处理。
# 而当update router，如设置外部网关时，l3才会去处理请求
# l3 agent使用service框架启动服务，其manager类为 neutron.agent.l3_agent.L3NATAgentWithStateReport，该类继承自L3NATAgent，
# 主要实现了基于rpc的_report_state向PluginReportStateAPI(topic为q-plugin)汇报状态信息，
# 这些信息由各个plugin来处理（比如ml2中通过start_rpc_listeners来注册该topic的消费者）。
# L3NATAgent类是最主要的L3 Manager类，该类继承关系为
# class L3NATAgent(firewall_l3_agent.FWaaSL3AgentRpcCallback, manager.Manager)；
# FWaaSL3AgentRpcCallback主要是加载防火墙驱动FWaaS Driver，并创建RPC与Plugin通信。
def main(manager='neutron.agent.l3.agent.L3NATAgentWithStateReport'):
    register_opts(cfg.CONF)
    common_config.init(sys.argv[1:])
    config.setup_logging()
    config.setup_privsep()
    server = neutron_service.Service.create(
        binary='neutron-l3-agent',
        topic=topics.L3_AGENT,
        report_interval=cfg.CONF.AGENT.report_interval,
        manager=manager)
    service.launch(cfg.CONF, server).wait()
