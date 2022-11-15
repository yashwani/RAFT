import json
import sys
import time
from communication import ZMQServer
from server import *


def start_server():
    external_port, internal_port, node_id, peer_ports, id_lookup = parse_config()

    server = Server(internal_port)

    zmqserver = ZMQServer(internal_port, peer_ports, server)

    server.init_rpc(zmqserver.send, zmqserver.broadcast)

    zmqserver.receive(internal_port)

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
