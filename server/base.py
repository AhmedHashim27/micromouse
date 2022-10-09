import random
from copy import deepcopy


class Maze:
    def __init__(self, array):
        self.array = array
        self.start = None
        self.end = None

    def fill(self):
        for row in range(len(self.array)):
            for col in range(len(self.array)):
                self.array[row][col] = Vertex((row, col), self)

    def connect(self):
        '''this function connects each vertex with the surrounding vertices'''
        for row in range(len(self.array)):
            for col in range(len(self.array)):
                vertex = self.array[row][col]
                vertex.connect() if vertex else None

    def print(self, status, current_vertex=None, orien=None):
        '''this functions prints the maze given 2 parameters:
        maze: the maze itself
        status: 0 --> weighted maze (the order of the vertices is shown (flood-fill) )
        1 (default) --> cleared maze (the path is shown as empty place and the walls as #'''

        direction_symbol = {0: "|^", 1: "<-", 2: "||", 3: "->"}  # symbols to represent the orientation
        temp_maze = deepcopy(self.array)

        if status:
            for row in range(len(self.array)):
                for col in range(len(self.array)):
                    vertex = self.array[row][col]
                    if vertex:
                        if len(str(vertex.order))==2:
                            temp_maze[row][col] = str(vertex.order)
                        elif len(str(vertex.order))==1:
                            temp_maze[row][col] = f"{vertex.order} "
                        else:
                            temp_maze[row][col] = "# "
                    else:
                        temp_maze[row][col] = "# "

        else:
            for row in range(len(self.array)):
                for col in range(len(self.array)):
                    vertex = self.array[row][col]
                    if vertex:
                        if vertex == current_vertex:
                            temp_maze[row][col] = direction_symbol[orien]
                        elif vertex == self.start:
                            temp_maze[row][col] = "S "
                        elif vertex == self.end:
                            temp_maze[row][col] = "E "
                        elif vertex.visited:
                            temp_maze[row][col] = "/ "
                        else:
                            temp_maze[row][col] = "  "
                    else:
                        temp_maze[row][col] = "# "


        for row in range(len(self.array)):
            print(temp_maze[row])


# Start of DFS vert object


class Vertex:
    def __init__(self, position, maze):
        self.position = position
        self.maze = maze
        self.visited = False
        self.updated = False
        self.order = None

    def connect(self):
        self.right = self.maze.array[self.position[0]][self.position[1]+1] if self.position[1] < len(self.maze.array)-1 else None
        self.up = self.maze.array[self.position[0]-1][self.position[1]] if self.position[0] > 0 else None
        self.left = self.maze.array[self.position[0]][self.position[1]-1] if self.position[1] > 0 else None
        self.down = self.maze.array[self.position[0]+1][self.position[1]] if self.position[0] < len(self.maze.array)-1 else None
        return 

    def neighbors(self):
        return random.sample([self.right, self.up, self.left, self.down],4)  # randomize the direction of movement

    def deal_neighbor(self, neighbor, command):
        '''this method does what the command says to the given neighbor:
            command --> 0 returns the neighbor vertex direction
            command --> 1 clears the neighbor vertex'''

        directions = {0: "up", 1: "left", 2: "down", 3: "right"}

        for i in range(4):
            if getattr(self, directions[i]) == neighbor:
                if command == 0:
                    return i
                setattr(self, directions[i], None)
        return None

    def __repr__(self):
        return f"vertex {self.position}"

    def __str__(self):
        return f"vertex {self.position}"

# End of DFS vertex object
