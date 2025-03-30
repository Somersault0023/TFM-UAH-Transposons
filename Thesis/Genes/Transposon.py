import random
from typing import List
from Genes.SnakeGene import *

class Transposon: pass
class SnakeChromosome:
    genes: List[SnakeGene]
    transposons: List[Transposon]
    
class Transposon:
    def __init__(self, gene: SnakeGene = None):
        self.gene = None
        self.migrate(gene,mutate=False)
        
    def migrate(self, newGene: SnakeGene, chromosome: SnakeChromosome=None, mutate=True):
        if self.gene is not None: self.gene.transposon = None

        self.gene = newGene
        if self.gene is not None:
            self.gene.transposon = self
            if mutate: self.mutateGene(chromosome)

    def mutateWeight(self,chromosome: SnakeChromosome):
        self.gene.mutate(True)
    def toggleExpression(self,chromosome: SnakeChromosome):
        self.gene.mutate(expressed = not self.gene.isExpressed)
    def mutateLayer(self,chromosome: SnakeChromosome):
        self.gene.mutate(newLayer = not self.gene.newLayer)

    def createNewGene(self,chromosome: SnakeChromosome):
        if self.gene is not None:
            nextGenes = chromosome.genes[self.gene.index+1:]
            for gene in nextGenes: gene.index += 1

            w = [Utils.random_unbounded_float() for _ in range(len(self.gene.weights))]
            chromosome.genes = chromosome.genes[:self.gene.index+1] + [SnakeGene(self.gene.index+1, weights=w)] + nextGenes

    def destroyGene(self,chromosome: SnakeChromosome):
        nextGenes = chromosome.genes[self.gene.index+1:]
        for gene in nextGenes: gene.index -= 1
        chromosome.genes = chromosome.genes[:self.gene.index] + nextGenes
        chromosome.transposons.remove(self)

    def mutateGene(self, chromosome):
        actionsList = [
            self.mutateWeight,
            self.toggleExpression,
            self.mutateLayer,
            self.createNewGene,
            #self.destroyGene
        ]
        actionsList[random.randint(0,len(actionsList)-1)](chromosome)