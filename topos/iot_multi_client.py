from core.topo import TopoParameter
from .multi_interface import MultiInterfaceTopo, MultiInterfaceConfig
import logging


class IoTMultiClientTopo(MultiInterfaceTopo):
    NAME = "IoTMultiClient"

    def __init__(self, topo_builder, parameterFile):
        logging.info("Initializing IoTMultiClientTopo...")
        super(IoTMultiClientTopo, self).__init__(
            topo_builder, parameterFile)

        for i in range(self.topo_parameter.clients):
            # For each client-router, add a client, a bottleneck link, and a server
            self.add_client_with_link()

        # And connect the router to all servers
        # for s in self.servers[1:]:
        #     self.add_link(self.router, s)

    def add_client_with_link(self):
        client = self.add_client()
        for bl in self.c2r_links:
            self.add_link(client, bl.get_left())

    def __str__(self):
        s = "IoT Multiple interface topology with several clients and servers\n"
        # i = 0
        # nc = len(self.get_client_to_router_links())
        # for i in range(0, nc):
        #     if i == nc // 2:
        #         s = s + "c-               r--s\n"
        #         s = s + "c-\sw---bl---sw-/ \-s\n"
        #     else:
        #         s = s + "c-/sw---bl---sw-\ /-s\n"

        print(self.client_count)
        return s


class IoTMultiClientConfig(MultiInterfaceConfig):
    NAME = "IoTMultiClient"

    def __init__(self, topo, param):
        super(IoTMultiClientConfig, self).__init__(topo, param)

    def configure_routing(self):
        super(IoTMultiClientConfig, self).configure_routing()
        for ci in range(len(self.clients)):
            for i, _ in enumerate(self.topo.c2r_links):
                # Routing for the congestion client
                cmd = self.add_global_default_route_command(self.get_router_ip_to_client_switch(i),
                                                            self.get_client_interface(ci, i))
                self.topo.command_to(self.clients[ci], cmd)

        for i, s in enumerate(self.topo.servers):
            # Routing for the congestion server
            cmd = self.add_simple_default_route_command(
                self.get_router_ip_to_server_switch(i))
            self.topo.command_to(s, cmd)

    def configure_interfaces(self):
        logging.info(
            "Configure interfaces using IoTMultiClientConfig...")
        super(IoTMultiClientConfig, self).configure_interfaces()
        self.clients = [self.topo.get_client(
            i) for i in range(0, self.topo.client_count())]
        self.servers = [self.topo.get_server(
            i) for i in range(0, self.topo.server_count())]
        netmask = "255.255.255.0"
        for ci in range(len(self.clients)):
            self.configure_client(ci)
            # for i, _ in enumerate(self.topo.c2r_links):
            #     # Congestion client
            #     cmd = self.interface_up_command(self.get_client_interface(
            #         ci, i), self.get_client_ip(i, ci), netmask)
            #     self.topo.command_to(self.clients[ci], cmd)
            #     client_interface_mac = self.clients[ci].intf(
            #         self.get_client_interface(ci, i)).MAC()
            #     self.topo.command_to(self.router, "arp -s {} {}".format(
            #         self.get_client_ip(i, ci), client_interface_mac))

            #     router_interface_mac = self.router.intf(
            #         self.get_router_interface_to_client_switch(i)).MAC()
            #     # Congestion client
            #     self.topo.command_to(self.clients[ci], "arp -s {} {}".format(
            #         self.get_router_ip_to_client_switch(i), router_interface_mac))

        for i, s in enumerate(self.servers):
            cmd = self.interface_up_command(self.get_router_interface_to_server_switch(i),
                                            self.get_router_ip_to_server_switch(i), netmask)
            self.topo.command_to(self.router, cmd)
            router_interface_mac = self.router.intf(
                self.get_router_interface_to_server_switch(i)).MAC()
            self.topo.command_to(s, "arp -s {} {}".format(
                self.get_router_ip_to_server_switch(i), router_interface_mac))
            cmd = self.interface_up_command(self.get_server_interface(
                i, 0), self.get_server_ip(interface_index=i), netmask)
            self.topo.command_to(s, cmd)
            server_interface_mac = s.intf(
                self.get_server_interface(i, 0)).MAC()
            self.topo.command_to(self.router, "arp -s {} {}".format(
                self.get_server_ip(interface_index=i), server_interface_mac))

    def configure_client(self, ci):
        netmask = "255.255.255.0"
        for i, _ in enumerate(self.topo.c2r_links):
            # Congestion client
            cmd = self.interface_up_command(self.get_client_interface(
                ci, i), self.get_client_ip(i, ci), netmask)
            self.topo.command_to(self.clients[ci], cmd)
            client_interface_mac = self.clients[ci].intf(
                self.get_client_interface(ci, i)).MAC()
            self.topo.command_to(self.router, "arp -s {} {}".format(
                self.get_client_ip(i, ci), client_interface_mac))

            router_interface_mac = self.router.intf(
                self.get_router_interface_to_client_switch(i)).MAC()
            # Congestion client
            self.topo.command_to(self.clients[ci], "arp -s {} {}".format(
                self.get_router_ip_to_client_switch(i), router_interface_mac))

    def get_client_ip(self, interface_index, client_index=100):
        return "{}{}.{}".format(self.param.get(TopoParameter.LEFT_SUBNET), interface_index, 5+client_index)

    def server_interface_count(self):
        return max(len(self.servers), 1)
