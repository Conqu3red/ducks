from typing import *
import math

class Data(NamedTuple):
    size: int
    nturns: int


def partitions(size):
    """
    size 5
    01234
    partition   4
            0 #----
            1 -#--- 3
            2 --#-- 2
            3 ---#- (duplicate)
            4 ----# (duplicate)
    
    """
    for cut_width in range(1, 2 + 1):
        for partition in range(math.ceil((size - cut_width + 1) / 2)):
            new_board = ()
            if size > cut_width:
                new_board = size - cut_width - partition,
            if partition > 0:
                new_board = *new_board, partition
            
            yield new_board
        # TODO: width 2 partitions


map = {}

x = 1

# this code doesn't work, please ignore for now.

while True:
    if x == 1:
        map[x] = 1, False
    else:
        for p in partitions(x):
            print(x, p, sum(map[n] for n in p) + 1)
        
        possibilites = [sum(map[n] for n in p) + 1 for p in partitions(x)]
        even = [p for p in possibilites if p % 2 == 0]
        odd = [p for p in possibilites if p % 2 == 1]
        if even:
            map[x] = min(even), 
        else:
            print("ODD")
            map[x] = min(odd)
            
        #map[x] = min()
    
    print(x, map[x])
    x += 1
    if x > 10: break
        