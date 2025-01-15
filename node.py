import socket
from multiprocessing import Process
import threading
import time
from timeit import default_timer as timer

class Node(Process):
    def __init__(self, node_id, neighbors, args):
        # Settings for crashing and type of election
        self.args = args
        self.crashed = False
        self.counter = 0

        # Sockets & Comunication attributes
        self.node_id = node_id      # The id of the node
        self.node_socket = 0        # The node's socket
        self.host_ip = socket.gethostbyname(socket.gethostname()) # The machine's IP, which will be the IP for all nodes in this case (might trigger anti virus)
        self.buffer_size = 512     # Max msg size
        self.encoding_format = 'utf-8'
        self.neighbors = neighbors  # THe node's accessible neighbors

        # Bully Leader Election Logic attributes
        self.leader = -1             # The leader this node has acknowledged
        self.in_election = 0        # Whether an election is occuring or not
        self.halt = False

        # Invitaiton Leader Election Logic attributes
        self.group = [self.node_id]
        self.is_leader = True       # Whether this node is the leader
        self.leaders = []

        # Metrics for report
        self.msgs_sent = 0

        self.node_loop()


    def send_msg(self, target_node_id, msg):
        if (len(msg) > self.buffer_size):
            print(f'[NODE {self.node_id}] MSG exceeded buffer')
            return 0
        try:
            msg = msg.encode(self.encoding_format)
            self.node_socket.sendto(msg, (self.host_ip, 6000 + target_node_id))
            self.msgs_sent += 1
        except:
            return 0
        return 1

    def receiving_msgs_thread(self):
        while not self.crashed:
            if self.counter == 1:
                break
            try:
                data = self.node_socket.recv(self.buffer_size)
                data = data.decode(encoding=self.encoding_format)

                if data and not self.crashed:
                    if self.args[1] == "BULLY":
                        if data.startswith("ARE-YOU-THERE"):
                            sender_id = int(data.split()[1])
                            if sender_id < self.node_id:
                                if self.send_msg(sender_id, f"YES"):
                                    self.msgs_sent += 1

                        elif data.startswith("HALT"):
                            self.halt = True
                        elif data.startswith("NEW-LEADER"):
                            sender_id = int(data.split()[1])
                            self.leader = sender_id
                        elif data.startswith("YES"):
                            self.halt = True
                   
                    elif self.args[1] == "PAPER":
                        if data.startswith("ARE-U-LEADER"):
                            sender_id = int(data.split()[1])
                            if self.is_leader:
                                self.send_msg(sender_id, f"I-AM-LEADER {self.node_id}")

                        elif data.startswith("INVITATION"):
                            sender_id = int(data.split()[1])
                            self.send_msg(sender_id, f"ACCEPT {self.node_id}")

                            if self.is_leader:
                                for member in self.group:
                                    if member != self.node_id:
                                        self.send_msg(member, f"INVITATION {sender_id}")

                        elif data.startswith("ACCEPT"):
                            sender_id = int(data.split()[1])
                            self.group.append(sender_id)

                        elif data.startswith("READY"):
                            self.is_leader = False
                            sender_id = int(data.split()[1])
                            self.send_msg(sender_id, f"ACK")

                        elif data.startswith("I-AM-LEADER"):
                            sender_id = int(data.split()[1])
                            self.leaders.append(sender_id)

            except:
                continue


    def start_invitation_election(self):
        self.leaders = []

        if not self.is_leader:
            # Insert ARE-U-THERE to leader msg implementation
            return  # Only leaders can start the invitation protocol.

        for neighbor in self.neighbors:
            self.send_msg(neighbor, f"ARE-U-LEADER {self.node_id}")

        if self.node_id == 0:
            time.sleep(65)  # Wait for responses
        if self.node_id == 1:
            time.sleep(55)  # Wait for responses
        if self.node_id == 2:
            time.sleep(45)  # Wait for responses
        if self.node_id == 3:
            time.sleep(35)  # Wait for responses
        if self.node_id == 4:
            time.sleep(25)  # Wait for responses
        if self.node_id == 5:
            time.sleep(3)  # Wait for responses


        if not self.is_leader:
            return
        
        if len(self.leaders) > 0:
            print(f"[NODE {self.node_id}] Starting invitation protocol.")
            for leaders in self.leaders:
                self.send_msg(leaders, f"INVITATION {self.node_id}")
            for member in self.group:
                if member != self.node_id:
                    self.send_msg(neighbor, f"INVITATION {self.node_id}")
        else:
            return
        
        for member in self.group:
            self.send_msg(member, f"READY {self.node_id}")
        print(f"[NODE {self.node_id}] Current group: {self.group}")
        self.is_leader = True


    def start_election_bully(self):
        self.leader = -1
        self.halt = False

        for target_id in self.neighbors:
            if target_id > self.node_id:
                if self.send_msg(target_id, f"ARE-YOU-THERE {self.node_id}"):
                    self.msgs_sent += 1

        time.sleep(2)  # Wait for responses

        if self.halt:
            print(f"[NODE {self.node_id}] Found a more suitable leader")
            return
        
        elif self.leader == -1:  # If no higher node responded, declare self as leader
            self.leader = self.node_id

            for target_id in self.neighbors:
                if self.halt:
                    return
                self.send_msg(target_id, f"NEW-LEADER {self.node_id}")

            print(f"[NODE {self.node_id}] Declares itself as leader")


    def create_socket(self):
        address = (self.host_ip, 6000 + self.node_id)
        self.node_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.node_socket.bind(address)
        self.node_socket.setblocking(False)
        print(f'Socket for node {self.node_id} was created, with port {6000 + self.node_id}')


    def node_loop(self):
        running = True
        self.create_socket()
        listening_thread = threading.Thread(target=self.receiving_msgs_thread)
        listening_thread.start()

        while running:
            if self.counter == 1:
                time.sleep(10)
                self.node_socket.shutdown(socket.SHUT_RDWR)
                self.node_socket.close()
                running = False
                listening_thread.join()
                break

            if self.args[1] == "BULLY":
                if not self.crashed:
                    start = timer()
                    self.start_election_bully()
                    end = timer()
                    time.sleep(5)
                    print(f"[NODE {self.node_id}] Acknowledged leader {self.leader}")
                    print(f"[NODE {self.node_id}] Sent {self.msgs_sent} messages")
                    print(f"[NODE {self.node_id}] Took {end-start:.8f} seconds to elect a leader")

                if self.args[2] == "CRASH":
                    
                    if self.node_id == self.leader:
                        self.leader == -1
                        print(f"[NODE {self.node_id}] CRASHED!")
                        self.crashed = True

            elif self.args[1] == "PAPER":
                if not self.crashed:
                    start = timer()
                    self.start_invitation_election()
                    end = timer()
                    time.sleep(5)
                    print(f"[NODE {self.node_id}] Is Leader: {self.is_leader}")
                    print(f"[NODE {self.node_id}] Sent {self.msgs_sent} messages")
                    print(f"[NODE {self.node_id}] Took {end-start:.8f} seconds to elect a leader")

                if self.args[2] == "CRASH":
                    
                    if self.node_id == self.leader:
                        self.leader == -1
                        print(f"[NODE {self.node_id}] CRASHED!")
                        self.crashed = True

            time.sleep(40)
            self.counter += 1
            

def main(node_id, neighbors, args):
    Node(node_id, neighbors, args)
    return