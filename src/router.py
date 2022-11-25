import const


class Router:

    def __init__(self, controller):

        self.controller = controller

    def route(self, msg):
        """ Route messages to controller for further action. """

        self.controller.all_server(msg)

        if msg["type"] == const.REQUEST_VOTE:
            return self.controller.respond_vote(msg)
        if msg["type"] == const.APPEND_ENTRIES_REQUEST:
            return self.controller.respond_append_entries(msg)