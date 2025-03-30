import numpy as np
from Genes.SnakeDNA import *
from Utils import Utils
import Utils.Constants as Consts

class SnakeGame: pass
class Snake:
    def __init__(self, brain: List[List[List[float]]]=None, DNA: SnakeChromosome = None):
        self.DNA = DNA if DNA is not None else SnakeChromosome(brain)
        self.brain = self.getPhenotype()
        
        self.body = [[0,0]]
        self.tupleBody = set()
        self.lastMove = Consts.Move.MOVES[0]
        self.fitness = -1
        self.applesEaten = 0

    def __str__(self): return str(self.body) + f"; Last Move: {self.lastMove}"

    def reset(self,boardWidth,boardHeight):
        x = random.randint(1,boardWidth-2)
        y = random.randint(1,boardHeight-2)

        self.lastMove = Consts.Move.MOVES[random.randint(0,len(Consts.Move.MOVES)-1)]
        self.body = [[x,y],[x-self.lastMove[0],y-self.lastMove[1]]]
        self.tupleBody = set(tuple(bodyPart) for bodyPart in self.body[1:])

    def move(self,input):
        dir = Utils.oneHotToDir(self.predict([input]))
        self.lastMove = Utils.DirToMove(dir,self.lastMove)
        newHead = [
            self.body[0][0] + self.lastMove[0], 
            self.body[0][1] + self.lastMove[1]
        ]

        self.tupleBody.remove(tuple(self.body[-1]))
        self.tupleBody.add(tuple(self.body[0]))
        self.body = [newHead] + self.body[:-1]
        return self.lastMove

    def addBodyPart(self,bodyPart):
        self.body.append(bodyPart)
        self.tupleBody.add(tuple(bodyPart))

    def predict(self,input):
        input = np.array(input)
        for layerIdx, layer in enumerate(self.brain): input = np.dot(input, np.array(layer))
        
        idx_1 = np.argmax(Utils.softmax(input).tolist()[0])
        return [1 if i == idx_1 else 0 for i in range(len(input[0]))]

    def getPhenotype(self) -> List[List[SnakeGene]]:
        brain = []
        curLayer = []
        for idx, gene in enumerate(self.DNA.genes):
            if gene.isExpressed:
                if idx > 0 and gene.newLayer:
                    brain.append(np.array(curLayer))
                    curLayer = []
                curLayer.append(gene.weights)
        brain.append(np.array(curLayer))
        return brain


# Mean number of layers: 5.6823
# Mean number of neurons per layer: 3.5197015293103147