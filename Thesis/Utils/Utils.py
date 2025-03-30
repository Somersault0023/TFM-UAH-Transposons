import math
import os
import sys
from matplotlib import pyplot as plt
import numpy as np
import pickle

if __name__ == "__main__": import Constants as Consts
else: import Utils.Constants as Consts

def random_unbounded_float(mean=0.0, stddev=1.0):
    """
    Generates a random float using a normal distribution with no specific bounds.

    Parameters:
    mean (float): The mean of the normal distribution (default is 0.0).
    stddev (float): The standard deviation of the normal distribution (default is 1.0).

    Returns:
    float: A random number with no specific bounds.
    """
    return np.random.normal(mean, stddev)

def softmax(input):
    exp_scores = np.exp(input - np.max(input))
    return exp_scores / np.sum(exp_scores)

import numpy as np

def sigmoid(input):
    def stableSigmoid(x):
        z = np.exp(-abs(x))
        return (1 if x >= 0 else z) / (1 + z)
    return np.array([stableSigmoid(x) for x in input])


def oneHotToDir(oneHot):
    return {
        "[1, 0, 0]": Consts.Dir.LEFT,
        "[0, 1, 0]": Consts.Dir.STRAIGHT,
        "[0, 0, 1]": Consts.Dir.RIGHT,
    }[str(oneHot)]

def DirToMove(dir,lastMove):
    moveIdx  = Consts.Move.MOVES_IDX[str(lastMove)]
    numMoves = len(Consts.Move.MOVES)
    idx = (moveIdx+dir+numMoves) % numMoves
    return [[ 0, 1, 0,-1][idx],[-1, 0, 1, 0][idx]]

def move_cursor(x, y):
    # Mover el cursor a la posición (x, y)
    sys.stdout.write(f"\033[{y+1};{x+1}H")

def clearScreen(): os.system('cls' if os.name == 'nt' else 'clear')

def saveSnake(snake, filename: str, display=False):
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory): os.makedirs(directory)

    with open(filename, 'wb') as file: pickle.dump(snake, file)
    if display: print(f"Snake saved in {filename}.")

def loadSnake(filename: str, display=False):
    with open(filename, 'rb') as file: snake = pickle.load(file)
    if display: print(f"Snake loaded from {filename}.")
    return snake

def loadGeneration(gen):
    return [loadSnake(f"SnakeGenerations/{getFormattedInt(gen,3)}/Snake_{getFormattedInt(i)}.pkl") for i in range(Consts.POPULATION_SIZE)]

def getFormattedInt(num,numDigits=2):
    string = ""
    aux = 1
    while aux < len(str(10**numDigits))-len(str(num)):
        aux += 1
        string  += "0"
    return string + str(num)

def getNearestObstacle(origin,snakeBody,move):
    x, y = origin
    distance = 0
    while 0 <= x < Consts.BOARD_WIDTH and 0 <= y < Consts.BOARD_HEIGHT:
        x += move[0]
        y += move[1]
        distance += 1
        if [x, y] in snakeBody: break
    return [x, y] 

def plotList(values: list, labels: list[str] = None, displayLabels=True):
    labels = [f"Serie {i}"if displayLabels else None for i in range(len(values))] if labels is None else labels
    for i, val in enumerate(values):
        plt.plot(range(len(val)), val, linestyle='-', label=labels[i])

    plt.xlabel('Índice')
    plt.ylabel('Valor')
    
    plt.title('Generation Fitness')
    
    plt.grid(True)
    plt.legend()
    plt.show()

def astar(snake, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    class Node():
        """A node class for A* Pathfinding"""

        def __init__(self, parent=None, position=None):
            self.parent = parent
            self.position = position

            self.g = 0
            self.h = 0
            self.f = 0

        def __eq__(self, other): return self.position == other.position

    # Create start and end node
    start_node = Node(position=snake.body[0])
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] >= Consts.BOARD_WIDTH or node_position[0] < 0 or node_position[1] >= Consts.BOARD_HEIGHT or node_position[1] < 0: continue

            # Make sure walkable terrain
            if tuple(node_position) in snake.tupleBody: continue

            children.append(Node(current_node, node_position))

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child: continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = child.position[0] - end_node.position[0] + child.position[1] - end_node.position[1] #((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g: continue
            open_list.append(child)

if __name__ == "__main__":
    MODE = "Transposons" #meanScores2 - Transposons_0.4
    VER = 0.4
    with open(f"Scores/meanScores2 - {MODE}_{VER}.txt",mode="r") as file:
        lines = file.read().split("], [")
        meanScores = [[float(val) for val in line.replace("[","").replace("]","").replace(" ","").split(",")] for line in lines]
        print(np.mean([execu[-1] for execu in meanScores]))
        plotList(meanScores,displayLabels=False)

    with open(f"Scores/bestScores2 - {MODE}_{VER}.txt",mode="r") as file:
        lines = file.read().split("], [")
        bestScores = [[float(val) for val in line.replace("[","").replace("]","").replace(" ","").split(",")] for line in lines]
        print(np.mean([execu[-1] for execu in bestScores]))
        plotList(bestScores,displayLabels=False)