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


