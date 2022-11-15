import zmq
from threading import Thread
import time
import json
from datetime import datetime

RCV_TIMEOUT = 2000


class ZMQServer:

    def __init__(self, port, peer_ports, server):
        self.peer_ports = peer_ports

        self.context = zmq.Context()
        self.sockets = self.init_sockets()

        self.reply = self.context.socket(zmq.REP)
        self.reply.bind("tcp://*:%s" % port)

        self.server = server

    def init_sockets(self):
        """ Initialize separate ZMQ REQ sockets for each peer. """

        sockets = {}

        for port in self.peer_ports:
            sockets[port] = self.context.socket(zmq.REQ)
            sockets[port].RCVTIMEO = RCV_TIMEOUT
            sockets[port].connect("tcp://localhost:%s" % port)

        return sockets

    def send(self, port, msg):
        """ Sends msg to peer port with timeout and return reply. """

        print(f"Sending to {port}", datetime.now())

        try:
            self.sockets[port].send_string(json.dumps(msg))
            reply = json.loads(self.sockets[port].recv())
            self.server.all_server(reply)
            # TODO router here too
            print("Received reply from ", port, "[", msg, "]")
        except Exception as e:
            print("Send failed to ", port)
            print(f"Exception on send: {e}", datetime.now())

            self.sockets[port].close()
            self.sockets[port] = self.context.socket(zmq.REQ)
            self.sockets[port].RCVTIMEO = RCV_TIMEOUT
            self.sockets[port].connect("tcp://localhost:%s" % port)
            reply = "Send fail"


        return reply

    def broadcast(self, msg):
        """ Send msg to all other servers and collect replies. """

        replies = {}

        for peer in self.peer_ports:
            replies[peer] = self.send(peer, msg)

        return replies

    def receive(self, port):
        """ Start receiver server in thread. """

        Thread(target=self.receiver).start()

    def receiver(self):
        """ Receiver server. """

        try:
            while True:
                msg = self.reply.recv()
                print("Received msg", datetime.now(), msg)

                print("Finished all server", datetime.now())
                reply_to_msg = self.server.router(json.loads(msg))

                print("Reply to msg", datetime.now(), reply_to_msg)
                self.reply.send_string(json.dumps(reply_to_msg))
                print("Send reply back", datetime.now())
        except:
            self.reply.close()
            self.context.destroy()
