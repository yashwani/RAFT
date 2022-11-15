from const import *

class State:
    def __init__(self, internal_port):
        self.role = FOLLOWER

        self.internal_port = internal_port

        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = {}
        self.match_index = {}

    def request_vote_req(self):
        return {
            "type": REQUEST_VOTE,
            "term": self.current_term,
            "candidate_id": self.internal_port,
            "last_log_index": self.log[-1]["index"] if len(self.log) > 0 else 0,
            "last_log_term": self.log[-1]["term"] if len(self.log) > 0 else 0
        }

    def request_vote_resp(self, vote):
        return {
            "type": REQUEST_VOTE_RESPONSE,
            "term": self.current_term,
            "vote_granted": vote
        }

    def append_entries_req(self):
        return {
            "type": APPEND_ENTRIES_REQUEST,
            "term": self.current_term,
        }

    def append_entries_resp(self):
        return {
            "type": APPEND_ENTRIES_RESPONSE,
            "term": self.current_term,
        }

