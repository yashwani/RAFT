import time

from state import State
from const import *
from timer import *
from datetime import datetime
from threading import Thread
import send


class Controller:
    def __init__(self, internal_port, size):
        self.internal_port = internal_port

        self.size = size

        self.state = State(internal_port)
        self.election_timer = ResettableTimer(self.to_candidate, 5000, 7000)
        self.to_follower()


    def init_rpc(self, send, broadcast):
        self.send = send
        self.broadcast = broadcast

    def router(self, msg):

        self.all_server(msg)

        if msg["type"] == REQUEST_VOTE:
            return self.state.request_vote_resp(self.decide_vote(msg))
        if msg["type"] == APPEND_ENTRIES_REQUEST:
            return self.respond_append_entries(msg)

    def all_server(self, msg):
        if msg["term"] > self.state.current_term:
            print("inside if statement")

            self.state.current_term = msg["term"]
            self.state.voted_for = None
            self.to_follower()

    def to_follower(self):
        print("TO FOLLOWER", datetime.now())

        self.state.role = FOLLOWER

        self.election_timer.reset()

    def to_candidate(self):
        print("TO CANDIDATE", datetime.now())

        self.state.current_term += 1
        self.votes = 1
        self.election_timer.reset()
        replies = self.broadcast(self.state.request_vote_req())
        if self.count_votes(replies):
            self.election_timer.cancel()
            self.to_leader()

    def to_leader(self):
        print("TO LEADER", datetime.now())

        Thread(self.heartbeat_thread()).start()

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

        for reply in replies.values():
            if "vote_granted" in reply:
                self.votes += reply["vote_granted"]

        return self.votes > self.size/2

    def respond_append_entries(self, msg):

        print("responding to append entries")

        self.election_timer.reset()

        return self.state.append_entries_resp()

    def heartbeat_thread(self):

        while True:

            time.sleep(HEARTBEAT_INTERVAL)

            replies = self.broadcast(self.state.append_entries_req())







