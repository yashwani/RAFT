import json
import sys
import time
from server import Server
from controller import *
import send
import zmq

"""

server - control logic
zmq server - receiver thread and sending 
state - state



"""

def start_server():
    external_port, internal_port, node_id, peers, id_lookup = parse_config()

    controller = Controller(internal_port, len(peers) + 1)

    context = zmq.Context()

    Server(internal_port, controller, context).recieve()

    sender = send.Sender(context, peers, controller)

    controller.init_rpc(sender.send, sender.broadcast)

    while True:
        time.sleep(0.1)


def parse_config():
    id_lookup = {}

    _this_file_name, config_path, node_id = sys.argv
    node_id = int(node_id)

    config_json = json.load(open(config_path))
    node_config = config_json["addresses"][node_id]
    ip, external_port, internal_port = node_config["ip"], node_config["external_port"], node_config["internal_port"]

    peer_ports = []
    for node_idx in range(len(config_json['addresses'])):
        if node_idx == node_id:
            continue
        other_config = config_json["addresses"][node_idx]
        id_lookup[other_config["internal_port"]] = node_idx
        peer_ports.append(other_config["internal_port"])

    return external_port, internal_port, node_id, peer_ports, id_lookup


if __name__ == "__main__":
    start_server()
