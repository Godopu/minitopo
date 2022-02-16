from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
import os
import threading


class BASICQUIC(RandomFileExperiment):
    NAME = "basicquic"
    SERVER_LOG = "echo-quic_server.log"
    CLIENT_LOG = "echo-quic_client.log"
    WGET_BIN = "wget"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        # Just rely on RandomFileExperiment
        super(BASICQUIC, self).__init__(
            experiment_parameter_filename, topo, topo_config)

    def load_parameters(self):
        # Just rely on RandomFileExperiment
        super(BASICQUIC, self).load_parameters()

    def prepare(self):
        super(BASICQUIC, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " +
                             BASICQUIC.CLIENT_LOG)
        self.topo.command_to(self.topo_config.server, "rm " +
                             BASICQUIC.SERVER_LOG)

    def getHTTPSServerCmd(self):
        # s = "{}/../utils/server".format(
        #     os.path.dirname(os.path.abspath(__file__)))
        s = "/home/mininet/pugit/sample/minitopo/utils/server & > {}".format(
            BASICQUIC.SERVER_LOG)

        print(s)
        return s

    def getHTTPSClientCmd(self):
        # s = "ping -c 3 -I {} {} > ping-result".format(
        #     "10.0.0.", self.topo_config.get_client_ip(1))

        # s = "{}/../utils/echo-client {} > {}".format(os.path.dirname(os.path.abspath(__file__)),
        #                                              self.topo.get_server_ip(
        #                                                  0),
        #                                              os.path.dirname(os.path.abspath(__file__)), BASICQUIC.CLIENT_LOG)

        s = "/home/mininet/pugit/sample/minitopo/utils/echo-client {} & > {}".format(
            self.topo_config.get_server_ip(0),
            BASICQUIC.CLIENT_LOG,
        )

        print(s)
        return s

    def clean(self):
        super(BASICQUIC, self).clean()

    def startServer(self):
        self.topo.command_to(self.topo_config.server, cmd)

    def run(self):
        cmd = self.getHTTPSServerCmd()
        self.topo.command_to(self.topo_config.server,
                             "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.router,
                             "netstat -sn > netstat_router_before")

        self.topo.command_to(self.topo_config.server, cmd)

        print("Waiting for the server to run")
        self.topo.command_to(self.topo_config.client, "sleep 2")
        # for i in range(1, self.topo.client_count()):
        #     self.topo.command_to(self.topo_config.clients[i], "sleep 2")

        cmd = self.getHTTPSClientCmd()
        # for c in self.topo_config.clients:
        #     self.topo.command_to(c, cmd)
        for i in range(1, self.topo.client_count()):
            self.topo.command_to(self.topo_config.clients[i], cmd)
            # self.topo_config.configure_client(i)

        self.topo.command_to(self.topo_config.server,
                             "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.router,
                             "netstat -sn > netstat_router_after")
        self.topo.command_to(self.topo_config.server,
                             "pkill -f server")
        self.topo.command_to(self.topo_config.client, "sleep 2")
