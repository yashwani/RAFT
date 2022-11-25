import zmq
from threading import Thread
import time
import json
from datetime import datetime

RCV_TIMEOUT = 1000


class ZMQServer:

    def __init__(self, port, peer_ports, server, context):
        self.peer_ports = peer_ports

        self.context = context
        # self.sockets = self.init_sockets()

        self.reply = self.context.socket(zmq.REP)
        self.reply.bind("tcp://*:%s" % port)

        self.server = server

    # def init_sockets(self):
    #     """ Initialize separate ZMQ REQ sockets for each peer. """
    #
    #     sockets = {}
    #
    #     for port in self.peer_ports:
    #         sockets[port] = self.context.socket(zmq.REQ)
    #         sockets[port].RCVTIMEO = RCV_TIMEOUT
    #         sockets[port].connect("tcp://localhost:%s" % port)
    #
    #     return sockets
    #
    # def send(self, port, msg):
    #     """ Sends msg to peer port with timeout and return reply. """
    #
    #
    #     try:
    #         self.sockets[port].send_string(json.dumps(msg))
    #         reply = json.loads(self.sockets[port].recv())
    #         self.server.all_server(reply)
    #     except Exception as e:
    #         self.sockets[port].close()
    #         self.sockets[port] = self.context.socket(zmq.REQ)
    #         self.sockets[port].RCVTIMEO = RCV_TIMEOUT
    #         self.sockets[port].connect("tcp://localhost:%s" % port)
    #
    #     return reply
    #
    # def broadcast(self, msg):
    #     """ Send msg to all other servers and collect replies. """
    #
    #     print("Broadcasting", msg)
    #
    #     replies = {}
    #
    #     for peer in self.peer_ports:
    #         replies[peer] = self.send(peer, msg)
    #
    #     return replies

    def receive(self):
        """ Start receiver server in thread. """

        Thread(target=self.receiver).start()

    def receiver(self):
        """ Receiver server. """

        try:
            while True:
                msg = self.reply.recv()
                reply_to_msg = self.server.router(json.loads(msg))

                self.reply.send_string(json.dumps(reply_to_msg))
        except:
            self.reply.close()
            self.context.destroy()
