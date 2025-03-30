import random
from typing import List
from Utils import Constants as Consts
from Utils import Utils
from Genes.SnakeGene import *
from Genes.Transposon import *

class SnakeChromosome:
    genes: List[SnakeGene]
    transposons: List[Transposon]
    def __init__(self, brain=None):
        if brain is not None:
            self.genes       = []
            self.transposons = []
            idx = 0
            for layer in brain:
                self.genes += [SnakeGene(idx+i,weights,i==0) for i,weights in enumerate(layer)]
                idx += len(layer)
        else:
            #Init genes without assigning weights:
            self.genes = [SnakeGene(i) for i in range(Consts.SNAKE_INPUTS + Consts.INITIAL_NEURONS + Consts.SNAKE_OUTPUTS)]

            #Making sure the first layer has the right number of neurons:
            for i in range(Consts.SNAKE_INPUTS+1):
                self.genes[i].newLayer = (i % Consts.SNAKE_INPUTS) == 0
                self.genes[i].isExpressed = True

            #Computing the size of the different layers:
            layerSizes = SnakeChromosome.getLayerSizes(self.genes)

            #Assigning weights to all the neurons, depending on the layer they are in:
            index = 1
            for gene in self.genes:
                if gene.newLayer:
                    nextLayerSize = layerSizes[index] #- (1 if index < len(layerSizes)-1 else 0)
                    index += 1
                gene.weights = [Utils.random_unbounded_float() for _ in range(nextLayerSize)]
        self.transposons = [Transposon() for _ in range(Consts.INITIAL_TRANSPOSONS)]
        for i in range(Consts.INITIAL_TRANSPOSONS): self.migrateTransposon(i)

    def getLayerSizes(chromosome):
        layerSizes = []
        curLayer = 0
        for gene in chromosome:
            if curLayer > 0 and gene.newLayer:
                layerSizes.append(curLayer)
                curLayer = 0
            curLayer += 1
        layerSizes += [curLayer,Consts.SNAKE_OUTPUTS]
        return layerSizes

    def __str__(self):
        return f"<SnakeChromosome\n   Genes: {[[g.value,g.newLayer,g.isExpressed] for g in self.genes]}\n>"
    
    def migrateTransposon(self,transposonIdx):
        gene = None
        while gene is None or gene.transposon is not None: gene = self.genes[random.randint(0,max(len(self.genes)-4,0))]
        self.transposons[transposonIdx].migrate(gene,mutate=False)