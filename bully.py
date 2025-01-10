import socket
import multiprocessing
import time

#Setting up github on a dif computer validation check

def node_process(node_id, num_nodes, port):
    def send_message(target_port, message):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), ("localhost", target_port))

    # Create a socket for receiving messages
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("localhost", port))
        sock.settimeout(1.0)  # Set a timeout of 1 second for recvfrom
        print(f"Node {node_id} listening on port {port}")

        leader = -1
        election_in_progress = False

        def start_election():
            nonlocal election_in_progress, leader
            if election_in_progress:
                return  # Prevent starting another election
            print(f"Node {node_id} starting election...")
            election_in_progress = True
            leader = -1
            for target_id in range(node_id + 1, num_nodes):
                send_message(5000 + target_id, f"ELECTION {node_id}")
            time.sleep(2)  # Wait for responses
            if leader == -1:  # If no higher node responded, declare self as leader
                leader = node_id
                election_in_progress = False
                print(f"Node {node_id} declares itself as leader")
                for target_id in range(num_nodes):
                    if target_id != node_id:
                        send_message(5000 + target_id, f"LEADER {node_id}")

        last_activity = time.time()
        while True:
            try:
                data, _ = sock.recvfrom(1024)
                message = data.decode()
                print(f"Node {node_id} received: {message}")

                if message.startswith("ELECTION"):
                    sender_id = int(message.split()[1])
                    if sender_id < node_id:
                        # Respond with "OK" and defer leadership decision
                        send_message(5000 + sender_id, "OK")
                        if not election_in_progress:
                            start_election()
                    elif sender_id > node_id:
                        election_in_progress = False  # Higher ID is taking over

                elif message.startswith("LEADER"):
                    received_leader = int(message.split()[1])
                    if received_leader > node_id or leader == -1:
                        leader = received_leader
                        election_in_progress = False
                        print(f"Node {node_id} recognizes leader as Node {leader}")

                elif message.startswith("OK"):
                    election_in_progress = True  # Acknowledge election ongoing

            except socket.timeout:
                # Timeout to detect leader absence
                if time.time() - last_activity > 5:  # No activity for 5 seconds
                    if leader == -1 and not election_in_progress:
                        print(f"Node {node_id} detecting leader absence.")
                        start_election()

            # Termination condition for testing: stop after 15 seconds of inactivity
            if time.time() - last_activity > 15:
                print(f"Node {node_id} terminating after timeout.")
                break

        print(f"Node {node_id} exiting.")




def test_bully_algorithm_sockets(num_nodes):
    processes = []
    for i in range(num_nodes):
        p = multiprocessing.Process(target=node_process, args=(i, num_nodes, 5000 + i))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


if __name__ == "__main__":
    test_bully_algorithm_sockets(2)
