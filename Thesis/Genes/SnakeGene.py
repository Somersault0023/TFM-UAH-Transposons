from typing import List
import random
from Utils import Constants as Consts, Utils

class Transposon: pass
class SnakeGene:
    transposon: Transposon
    def __init__(self, index: int, weights: List[float]=None, newLayer: bool=None, expressed:bool=True):
        self.index   = index
        self.weights = weights

        if newLayer is not None: self.newLayer = newLayer 
        else: self.newLayer = index == 0 or random.random() < Consts.PROB_NEW_LAYER

        self.isExpressed = expressed
        self.transposon  = None

    def mutate(self, mutateVal=False, newLayer=None, expressed=None):
        if mutateVal: self.weights[random.randint(0,len(self.weights)-1)] = Utils.random_unbounded_float()
        if newLayer is not None:  self.newLayer    = newLayer
        if expressed is not None: self.isExpressed = expressed