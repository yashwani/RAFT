import zmq
import const
import json


class Sender:

    def __init__(self, context, peers, server):

        self.peers = peers
        self.context = context
        self.sockets = self.sockets()
        self.server = server

    def sockets(self):
        """ Initialize separate ZMQ REQ sockets for each peer. """

        sockets = {}

        for port in self.peers:
            sockets[port] = self.context.socket(zmq.REQ)
            sockets[port].RCVTIMEO = const.RCV_TIMEOUT
            sockets[port].connect("tcp://localhost:%s" % port)

        return sockets

    def send(self, port, msg):
        """ Sends msg to peer port with timeout and return reply. """

        print("Attempting send", msg)

        try:
            self.sockets[port].send_string(json.dumps(msg))
            reply = json.loads(self.sockets[port].recv())
            self.server.all_server(reply)
        except Exception as e:
            self.sockets[port].close()
            self.sockets[port] = self.context.socket(zmq.REQ)
            self.sockets[port].setsockopt(zmq.LINGER, 0)
            self.sockets[port].RCVTIMEO = const.RCV_TIMEOUT
            self.sockets[port].connect("tcp://localhost:%s" % port)
            reply = "rep req failed"

        return reply

    def broadcast(self, msg):
        """ Send msg to all other servers and collect replies. """

        replies = {}

        for peer in self.peers:
            replies[peer] = self.send(peer, msg)

        return replies