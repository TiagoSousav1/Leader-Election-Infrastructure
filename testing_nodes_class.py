import concurrent.futures
import multiprocessing
import node

if __name__=='__main__':
    nodes_args = [[0, None], [1, None]]
    
    p1 = multiprocessing.Process(target=node.main, args=nodes_args[0])
    p2 = multiprocessing.Process(target=node.main, args=nodes_args[1])

    p1.start()
    p2.start()

    p1.join()
    p2.join()