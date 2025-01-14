import multiprocessing
import node
import sys

if __name__=='__main__':
    graph = { 
                0 : [1, 2, 3, 4, 5],
                1 : [0, 2, 3, 4, 5],
                2 : [0, 1, 3, 4, 5],
                3 : [0, 1, 2, 4, 5],
                4 : [0, 1, 2, 3, 5],
                5 : [0, 1, 2, 3, 4],
            } 
    proccesses = []

    for node_neighbour in graph:
        p = multiprocessing.Process(target=node.main, args=[node_neighbour, graph[node_neighbour], sys.argv])
        p.start()
        proccesses.append(p)

    for p in proccesses:
        p.join()