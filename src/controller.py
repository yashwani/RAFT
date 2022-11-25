import time
from const import *
import timer
from datetime import datetime
from threading import Thread


class Controller:
    def __init__(self, internal_port, size, state, sender, messages):
        """ Start election timer and switch to foller state. """
        self.internal_port = internal_port
        self.size = size
        self.state = state
        self.messages = messages

        self.election_timer = timer.ResettableTimer(self.to_candidate, 5000, 7000)
        self.send = sender.send
        self.broadcast = sender.broadcast

        self.to_follower()

    def all_server(self, msg):
        """ RAFT rules for all servers. """

        if msg[TERM] <= self.state.current_term:
            return

        self.state.current_term = msg[TERM]
        self.state.voted_for = None
        self.to_follower()

    def all_server_broadcast(self, msgs):
        """ RAFT rules for all servers on reciept of broadcasts. """

        for msg in msgs.values():
            self.all_server(msg)

    def to_follower(self):
        """ Rules upon switching to follower state. """

        print("TO FOLLOWER", datetime.now())

        self.state.role = FOLLOWER

        self.election_timer.reset()

    def to_candidate(self):
        """ Rules upon switching to candidate state. """
        print("TO CANDIDATE", datetime.now())

        self.state.current_term += 1
        self.votes = 1

        self.election_timer.reset()

        replies = self.broadcast(self.messages.request_vote_req())
        self.all_server_broadcast(replies)
        if self.count_votes(replies):
            self.election_timer.cancel()
            self.to_leader()

    def to_leader(self):
        """ Rules upon switching to leader state. """
        print("TO LEADER", datetime.now())

        Thread(self.heartbeat_thread()).start()

    def decide_vote(self, msg):
        """ Decide whether to grant vote. """

        if self.state.current_term < msg["term"]:
            return False

        if msg[LAST_LOG_TERM] < (self.state.log[-1][TERM] if len(self.state.log) > 0 else 0):
            return False

        if msg[LAST_LOG_INDEX] < (self.state.log[-1][INDEX] if len(self.state.log) > 0 else 0):
            return False

        if self.state.voted_for is not None and self.state.voted_for != msg[CANDIDATE_ID]:
            return False

        return True

    def count_votes(self, replies):
        """ Returns True if wins election, False otherwise. """

        for reply in replies.values():
            if VOTE_GRANTED in reply:
                self.votes += reply[VOTE_GRANTED]

        return self.votes > self.size / 2

    def respond_vote(self, msg):
        """ Response to a Request Vote message. """

        grant = self.decide_vote(msg)

        return self.messages.request_vote_resp(grant)

    def respond_append_entries(self, msg):
        """ Response to an Append Entries message.  """

        self.election_timer.reset()

        return self.messages.append_entries_resp()

    def heartbeat_thread(self):
        """ Frequent heartbeat messages sent by leader to maintain authority. """

        while True:

            time.sleep(HEARTBEAT_INTERVAL)

            replies = self.broadcast(self.messages.append_entries_req())
            self.all_server_broadcast(replies)
