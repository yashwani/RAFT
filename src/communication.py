import zmq
from threading import Thread
import time

RCV_TIMEOUT = 3000

class ZMQServer:

    def __init__(self, port, peer_ports):
        self.context = zmq.Context()
        self.sockets = self.init_sockets(peer_ports)

        self.reply = self.context.socket(zmq.REP)
        self.reply.bind("tcp://*:%s" % port)

    def init_sockets(self, peer_ports):
        """ Initialize separate ZMQ REQ sockets for each peer. """
        sockets = {}

        for port in peer_ports:
            sockets[port] = self.context.socket(zmq.REQ)
            sockets[port].connect("tcp://localhost:%s" % port)
            sockets[port].RCVTIMEO = RCV_TIMEOUT

        return sockets

    def send(self, port, msg):
        """ Sends msg to peer port with timeout and return reply. """

        try:
            self.sockets[port].send_string(msg)
            reply = self.sockets[port].recv()
            print("Received reply from ", port, "[", msg, "]")
        except:
            self.sockets[port].close()
            self.sockets[port] = self.context.socket(zmq.REQ)
            self.sockets[port].RCVTIMEO = RCV_TIMEOUT
            self.sockets[port].connect("tcp://localhost:%s" % port)
            reply = "Send fail"
            print("Send failed to ", port)

        return reply

    def broadcast(self, msg):
        """ Send msg to all other servers and collect replies. """
        replies = None
        return replies

    def receive(self, port):
        """ Start receiver server in thread. """
        Thread(target=self.receiver, args=[port]).start()

    def receiver(self, port):
        """ Receiver server. """

        try:
            while True:
                msg = self.reply.recv()
                print("Received request: ", msg)
                time.sleep(1)
                self.reply.send_string("World from %s" % port)
        except:
            self.reply.close()
            self.reply.term()
            self.context.destroy()