import socket
from multiprocessing import Process
import threading
import time


class Node(Process):
    def __init__(self, node_id, neighbors):

        # Sockets & Comunication attributes
        self.node_id = node_id      # The id of the node
        self.node_socket = 0        # The node's socket
        self.host_ip = socket.gethostbyname(socket.gethostname()) # The machine's IP, which will be the IP for all nodes in this case (might trigger anti virus)
        self.buffer_size = 2048     # Max msg size

        # Leader Election Logic attributes
        self.leader = 0             # The leader this node has acknowledged
        self.in_election = 0        # Whether an election is occuring or not
        self.neighbors = neighbors  # THe node's accessible neighbors

        self.node_loop()


    def send_msg(self, node_id, msg):
        if (len(msg) > self.buffer_size):

            print(f'[NODE {self.node_id}] MSG exceeded buffer')
            return 0
        
        self.node_socket.sendto(msg, (self.host_ip, 5000 + node_id))
        return 1

    def receiving_msgs_thread(self):
        while True:
            data, addr = self.node_socket.recvfrom(self.buffer_size)
            print(f'Node {self.node_id} Received: {data}')

    def start_election(self):
        pass

    def create_socket(self):
        address = (self.host_ip, 5000 + self.node_id)
        self.node_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.node_socket.bind(address)
        print(f'Socket for node {self.node_id} was created, with port {5000 + self.node_id}')


    def node_loop(self):
        running = True
        self.create_socket()
        listening_thread = threading.Thread(target=self.receiving_msgs_thread)
        listening_thread.start()

        time.sleep(1)

        while running:
            if self.node_id == 1:
                self.send_msg(0, b'Hello World!')
            else:
                self.send_msg(1, b'Hello World!')
            time.sleep(10)
            pass


def main(node_id, neighbors):
    Node(node_id, neighbors)
    return