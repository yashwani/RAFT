from state import State
from const import *
from timer import *
from datetime import datetime


class Server:
    def __init__(self, internal_port):
        self.internal_port = internal_port

        self.state = State(internal_port)
        self.election_timer = ResettableTimer(self.to_candidate, 5000, 7000)
        self.to_follower()

    def init_rpc(self, send, broadcast):
        self.send = send
        self.broadcast = broadcast

    def router(self, msg):

        print("Router received msg", datetime.now(), msg)

        self.all_server(msg)

        if msg["type"] == REQUEST_VOTE:
            print("Received request to vote", datetime.now())
            return self.state.request_vote_resp(self.decide_vote(msg))
        if msg["type"] == APPEND_ENTRIES_REQUEST:
            return self.respond_append_entries(msg)

    def all_server(self, msg):
        print("All server rule", datetime.now())
        if msg["term"] > self.state.current_term:
            print("inside if statement")

            self.state.current_term = msg["term"]
            self.to_follower()

        print("finished inside all server", datetime.now())

    def to_follower(self):
        print("TO FOLLOWER", datetime.now())

        self.state.role = FOLLOWER

        if self.internal_port == 51701:
            return

        self.election_timer.reset()

    def to_candidate(self):
        print("TO CANDIDATE", datetime.now())

        self.state.current_term += 1
        self.votes = 1
        self.election_timer.reset()
        replies = self.broadcast(self.state.request_vote_req())
        if self.count_votes(replies):
            self.to_leader()

    def to_leader(self):
        print("TO LEADER", datetime.now())

        replies = self.broadcast(self.state.request_vote_req())

    def decide_vote(self, msg):
        """ RequestVote RPC receiver implementation that decide whether to grant vote. """

        if self.state.current_term < msg["term"]:
            return False

        if msg["last_log_term"] < (self.state.log[-1]["term"] if len(self.state.log) > 0 else 0):
            return False

        if msg["last_log_index"] < (self.state.log[-1]["index"] if len(self.state.log) > 0 else 0):
            return False

        if self.state.voted_for is not None and self.state.voted_for != msg["candidate_id"]:
            return False

        return True


    def count_votes(self, replies):
        """ Returns True if wins election, False otherwise. """

        self.votes = 0

        for reply in replies.values():
            if "vote" in reply:
                self.votes += reply["vote"]

        return self.votes > SIZE/2

    def respond_append_entries(self, msg):

        self.election_timer.reset()

        return self.state.append_entries_resp()




