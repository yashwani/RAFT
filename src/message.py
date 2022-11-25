from const import *


class Message:

    def __init__(self, state):
        self.state = state

    def request_vote_req(self):
        return {
            TYPE: REQUEST_VOTE,
            TERM: self.state.current_term,
            CANDIDATE_ID: self.state.internal_port,
            LAST_LOG_INDEX: self.state.log[-1][INDEX] if len(self.state.log) > 0 else 0,
            LAST_LOG_TERM: self.state.log[-1][TERM] if len(self.state.log) > 0 else 0
        }

    def request_vote_resp(self, vote):
        return {
            TYPE: REQUEST_VOTE_RESPONSE,
            TERM: self.state.current_term,
            VOTE_GRANTED: vote
        }

    def append_entries_req(self):
        return {
            TYPE: APPEND_ENTRIES_REQUEST,
            TERM: self.state.current_term,
        }

    def append_entries_resp(self):
        return {
            TYPE: APPEND_ENTRIES_RESPONSE,
            TERM: self.state.current_term,
        }
