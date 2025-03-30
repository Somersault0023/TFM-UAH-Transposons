BOARD_WIDTH  = 20
BOARD_HEIGHT = 20

POINTS_PER_APPLE = 100

SNAKE_INPUTS  = 11
SNAKE_OUTPUTS = 3

INITIAL_NEURONS     = 20
INITIAL_TRANSPOSONS = 3
PROB_NEW_LAYER      = 0.23

POPULATION_SIZE = 100
PROB_CROSSOVER  = 0.9
PROB_MUTATION   = 0.01

USE_TRANSPOSONS = True
FIRST_TRANSPOSON_GENERATION = 40
MAX_PROB_TRANSPOSON_MUTATION = 0.4

SAVE_GENERATIONS = False
SAVE_EVERY_GENERATION = False

KEEP_BEST_SNAKE = True

class Move:
    UP    = 0
    RIGHT = 1
    DOWN  = 2
    LEFT  = 3

    MOVES = [
        [ 0,-1],
        [ 1, 0],
        [ 0, 1],
        [-1, 0],
    ]

    MOVES_IDX = {
        "[0, -1]": UP,
        "[1, 0]":  RIGHT,
        "[0, 1]":  DOWN,
        "[-1, 0]": LEFT,
    }

class Dir:
    LEFT     = -1
    STRAIGHT =  0
    RIGHT    =  1

    DIRS = [
        LEFT,
        STRAIGHT,
        RIGHT
    ]