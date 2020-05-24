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

from neutron.agent import l3_agent


# Neutron L3 Agent(Layer-3 Networking Extension)作为一种API扩展（通过API来创建router或者floating ip，以提供路由以及NAT的功能），
# 向租户提供了路由和NAT功能。l3扩展包含两种资源：
#    router：在不同内部子网中转发数据包；通过指定内部网关做NAT。每一个子网对应router上的一个端口，这个端口的ip就是子网的网关。
#    floating ip：代表一个外部网络的IP，映射到内部网络的端口上。当网络的router:external属性为True时，floating ip才能定义。
# 这两种资源都对应有不同的属性。支持CRUD操作。

# 使用步骤
# 1. 租户通过horizon，nova命令或者自定义的脚本，发送与router或floating ip相关的操作。
# 2. 这些API请求发送到neutron server，通过neutron提供的API extension相对应。
# 3. 实现这些API extension的操作，比如说create_router，则由具体的plugin和database来共同完成。
# 4. plugin会通过rpc机制与计算网络节点上运行的l3 agent来执行l3 转发和NAT的功能。
def main():
    l3_agent.main()
