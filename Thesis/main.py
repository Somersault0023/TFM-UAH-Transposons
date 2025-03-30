from Snake.SnakeFarm import *
from Snake.SnakeGame import *

import Utils.Constants as Consts
import Utils.Utils as Utils

MODE = "Transposons" if Consts.USE_TRANSPOSONS else "Standard"
VER = 0.4

NUMBER_OF_EXECS = 20
NUMBER_OF_GENS  = 200

TRAIN_OR_PLAY = False

if TRAIN_OR_PLAY:
    Utils.clearScreen()
    meanScores = []
    bestScores = []
    for i in range(NUMBER_OF_EXECS):
        initGen = 0
        farm = SnakeFarm() # Utils.loadGeneration(initGen)
        for ii in range(NUMBER_OF_GENS): farm.runGeneration(initGen+ii+1,False,bestSnakeName=f"BestSnakes/{MODE}_{i+1}")
        
        print(f"\n{'\n'.join(['' for _ in range(i+1)])}EXECUTION {i}: Best Snake -> [Fitness: {Utils.getFormattedInt(round(farm.prevBestSnake.fitness),1)}]")
        meanScores.append(farm.meanScores)
        bestScores.append(farm.bestScores)

    with open(f"Scores/meanScores3 - {MODE}_{VER}.txt", mode="w") as file: file.write(str(meanScores))
    with open(f"Scores/bestScores3 - {MODE}_{VER}.txt", mode="w") as file: file.write(str(bestScores))
    farm.saveCurSnakes(ii,f"BestSnakes2/{MODE}_{i}")
    Utils.plotList(meanScores,displayLabels=False)
    Utils.plotList(bestScores,displayLabels=False)
else:
    """
    SNAKE_NAME = "Transposons_10 - 4929"
    snake = Utils.loadSnake(f"SnakeGenerations/BestSnakes/{SNAKE_NAME}.pkl") #Snake(Utils.loadSnake(f"brain - 4963.pkl")) #
    #Utils.saveSnake(snake,"SnakeGenerations/BestSnakes/Standard_6 - 4963.pkl") #
    game = SnakeGame(20,20,Utils.loadSnake(f"SnakeGenerations/BestSnakes/{SNAKE_NAME}.pkl"))
    """
    
    for i in range(10):
        game = SnakeGame(20,20,Snake())
        game.start(forcePlay=True)