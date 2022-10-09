import os
import time
from base import Maze


def localize(where_am_i, orien, maze, start=False, surr=None, run=0):
    '''this function returns the direction of movement given three variables:
       where_am_i = a tuple of x,y --> (x,y)
       orien = from 0 to 4 (the absolute orientation is facing forward (0) (1 --> left) (2 --> backward) (3 --> right))
       surr = a tuple of the surrounding blocks (up,left,down,right) --> 1 if the block is clear (can move there),
        0 or None if a wall is detected.'''

    # where_am_i = calibrate_tuple(where_am_i,1) #reverse the x , y coordinates
  
    current_vertex = maze.array[where_am_i[0]][where_am_i[1]]
    maze.print(0, current_vertex, orien)

    if run:
        for neighbor in current_vertex.neighbors():
            if neighbor:
                if not (current_vertex.order - (neighbor.order+1)):
                    time.sleep(1)
                    from_to(current_vertex, neighbor, orien, maze, 0, run=1)
    
    if not current_vertex.visited:
        current_vertex.visited = True
        if start:
            maze.start = current_vertex
            current_vertex.updated = True

        history.append(current_vertex)
        print(f"\nPath history: {history}\nOrientation: {orien}\n")

        if not surr:
            error = True
            while error:
                try:
                    surr = tuple(map(int, [ch for ch in input("Enter the surroundings: ")]))  # get the surroundings from the user (these will be obtained from the sensors later)
                    if len(surr) >4:
                        current_vertex.order = 0
                        maze.end = current_vertex
                        surr = surr[:-1]
                except ValueError:
                    print("\nOnly numbers are accepted")
                else:
                    if len(surr) < 4:
                        print("\n4 numbers at least required")
                    else:
                        error = False    
        os.system('cls')
        surr = calibrate_tuple(surr, orien)
        update_vertex(current_vertex, surr, maze)
        dfs(current_vertex,orien, maze)

    time.sleep(1)
    return orien


def calibrate_tuple(to_rotate, factor):
    '''this function rotates a tuple (surr),(where_am_i) by a given number(orien),(1)
    in order to align the micro-mouse with the maze'''

    while factor >= len(to_rotate):
        factor = factor - len(to_rotate)
    return to_rotate[-factor:] + to_rotate[:-factor]


def update_vertex(vertex, surr, maze):
    '''this function updates each vertex with the correct information received from the micro-mouse
       whether it is a wall or not --We assumed earlier that all vertices in the maze are open (not walls)'''

    directions = {0: "up", 1: "left", 2: "down", 3: "right"}
    for i in range(4):
        neighbor_vertex = getattr(vertex,directions[i])
        if neighbor_vertex:
            if not neighbor_vertex.updated:
                if not (neighbor_vertex and surr[i]):  # check if the received status is the same as the assumed one 
                    maze.array[neighbor_vertex.position[0]][neighbor_vertex.position[1]] = None  # set the block as a wall
                neighbor_vertex.updated = True  # flag the vertex as updated (future updates will be ignored)
    maze.connect()  # reconnect the vertices


def dfs(vertex,orien,maze):
    '''this function implements DFS to make sure each block is visited (it points to the next block to be visited)'''
    for neighbor in vertex.neighbors():
        if neighbor and (not neighbor.visited):
            from_to(vertex, neighbor, orien, maze)
    return vertex


def from_to(location, destination,orien, maze, from_dfs=1, run=0):
    
    global history
    directions = ("in front of me","to my left","behind me","to my right")
    condition = destination in history[-1].neighbors() if from_dfs else destination in location.neighbors()

    if condition:
        direction = location.deal_neighbor(destination, 0)
        print(f"I am in {location} and moving to {destination} which is {calibrate_tuple(directions, orien)[direction]} {orien}\n")
        return localize(destination.position, direction, maze, run=run)

    reversed_path = list(reversed(history[history.index(location):-1]))
    location = history[-1]

    for prev_vertex in reversed_path:
        orien = from_to(location, prev_vertex,orien, maze, 0)
        location = prev_vertex

    history = history[:history.index(location)+1]
    return from_to(location, destination, orien, maze)


def flood_fill(maze,vertex,order):
    '''this function flood-fills the maze to get the shortest path from start to end only'''
    for neighbor in vertex.neighbors():
        if neighbor:
            if neighbor.order == None:
                neighbor.order = order +1
                flood_fill(maze, neighbor, neighbor.order)
    return


def main():
    array= [[0,0,0,0,0,0,0,0,0],  # 9x9
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0]]  ## this is temporary (hard-coded for trial)

    maze = Maze(array)
    maze.fill()
    maze.connect()

    global history
    history = []

    localize((8,1), 0, maze, True)  # initiate the first step
    print("Flood-filling the maze:\n")
    flood_fill(maze, maze.end, 0)
    maze.print(1)
    print("\n Solving the maze\n")
    localize(maze.start.position, 0, maze, run=1)
    
main()
