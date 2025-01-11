import concurrent.futures
import multiprocessing
import node


if __name__=='__main__':
    graph = { 
                0 : [1, 3, 4],
                1 : [2, 3],
                2 : [],
                3 : [1, 2],
                4 : [],
                5 : [1, 2],
            } 
    proccesses = []

    for node_neighbour in graph:
        p = multiprocessing.Process(target=node.main, args=[node_neighbour, graph[node_neighbour]])
        p.start()
        proccesses.append(p)

    for p in proccesses:
        p.join()