import json
from threading import Thread
import zmq


class Server:

    def __init__(self, port, controller, context):

        self.context = context
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)

        self.controller = controller

    def recieve(self, router):
        """ Starts a receiver server in a thread. """

        Thread(target=self.receiver, args=[router]).start()

    def receiver(self, router):
        """ Receiver server. """

        try:
            while True:
                msg = self.socket.recv()
                reply_to_msg = router.route(json.loads(msg))

                self.socket.send_string(json.dumps(reply_to_msg))
        except:
            self.socket.close()
            self.context.destroy()
