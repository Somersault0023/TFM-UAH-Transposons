from numpy import array
from Snake.Snake import *
from Snake.SnakeGame import *
import copy
import statistics as Stats
import Utils.Constants as Consts
import Utils.Utils as Utils

class SnakeFarm:
    def __init__(self, snakes: List[Snake]=None):
        self.snakes = snakes if snakes is not None else [Snake() for i in range(Consts.POPULATION_SIZE)]
        self.game = SnakeGame(snake=self.snakes[0])
        self.meanScores = []
        self.bestScores = []
        self.prevBestSnake = None
        self.currBestSnake = None
        self.lastBigImprovement = 0

    def saveCurSnakes(self,curGen,bestSnakeName="BestSnake"):
        if Consts.SAVE_GENERATIONS:
            pop = self.snakes[:]
            pop.sort(key=lambda snake: -snake.fitness)

            for idx,snake in enumerate(pop if curGen % 50 == 0 else [pop[0]]):
                Utils.saveSnake(snake,f"SnakeGenerations/{Utils.getFormattedInt(curGen,3)}/Snake_{Utils.getFormattedInt(idx)}.pkl")

        Utils.saveSnake(self.currBestSnake,f"SnakeGenerations/{bestSnakeName}.pkl")
    
    def evaluateSnakes(self, g=None,display=True, displayGeneration=False):
        ret = False
        if display: Utils.clearScreen()
        for i,snake in enumerate(self.snakes):
            if snake.fitness == -1:
                self.game.reset(snake)
                f = 0
                for ii in range(5): f += self.game.start(display,g)
                snake.fitness = f/5

            if self.currBestSnake is None or snake.fitness > self.currBestSnake.fitness:
                self.currBestSnake = copy.deepcopy(snake)
                ret = True

        if displayGeneration: Utils.clearScreen()
        s = []
        for i,snake in enumerate(self.snakes):
            s.append(snake.fitness)
            if displayGeneration:
                gen = f"-gen{g}" if g is not None else ""
                print(f"[SNAKE {i}{gen}]: Score -> {round(snake.fitness,2)} | Apples eaten: {len(snake.applesEaten)} ({snake.applesEaten})")

        self.snakes.sort(key=lambda snake: snake.fitness)
        if Consts.KEEP_BEST_SNAKE and self.prevBestSnake is not None: self.snakes[0] = copy.deepcopy(self.prevBestSnake)
        self.meanScores.append(Stats.mean(s))
        self.bestScores.append(self.currBestSnake.fitness)
        return ret

    def rouletteWheel(self):
        #pop = self.snakes[:]
        #pop.sort(key=lambda snake: snake.fitness)

        #supposing the snake list is already sorted:
        newPop = list(map(lambda snake: snake.fitness, self.snakes))
        totalFitness = sum(newPop)
        mate_pool = random.choices(self.snakes,[newPop[i] / totalFitness for i in range(len(self.snakes))], k=len(self.snakes))

        return mate_pool
    
    def crossover(self):
        mate_pool = self.rouletteWheel()

        offspring_pop = []
        for i in  range(0,len(self.snakes) - 1,2):
            parent1 = mate_pool[i]
            parent2 = mate_pool[i+1]
            offspring = self.recombination(parent1,parent2)
            offspring_pop.extend(offspring)

        self.snakes = offspring_pop

    def generateOffspring(self,firstHalf: List[array],secondHalf: List[array]):
        diff = len(secondHalf[0]) - len(firstHalf[-1][0])
        if diff != 0:
            newLastLayer = []
            if diff > 0:
                for i,weights in enumerate(firstHalf[-1]):
                    newLastLayer.append(np.concatenate((firstHalf[-1][i],[Utils.random_unbounded_float() for _ in range(diff)])))
            elif diff < 0:
                for i,weights in enumerate(firstHalf[-1]):
                    newLastLayer.append(array(list(weights)[:diff]))
            firstHalf[-1] = array(newLastLayer)

        #To do: falta incorporar los transposones
        offspringDNA = SnakeChromosome(firstHalf+secondHalf)
        return Snake(DNA=offspringDNA)

    def recombination(self,parent1:Snake,parent2:Snake):
        minLen = min(len(parent1.brain),len(parent2.brain))
        if random.random() < Consts.PROB_CROSSOVER:
            pointIdx = random.randint(1,minLen-1)
            return [
                self.generateOffspring(parent1.brain[:pointIdx],parent2.brain[pointIdx:]),
                self.generateOffspring(parent2.brain[:pointIdx],parent1.brain[pointIdx:])
            ]
        else: return [parent1,parent2]

    def getStagnationRatio(self, x, y):
        """
        Calculates the stagnation index for a sublist of self.meanScores[x:y].

        Args:
            x (int): Starting index of the range to analyze.
            y (int): Ending index of the range to analyze (exclusive).

        Returns:
            float: A value between 0 and 1, where 0 indicates evolution and 1 indicates stagnation.
        """
        tramo = self.meanScores[x:y]
        if len(tramo) < 2: return 0.0
        
        ruido = np.std(tramo)
        if ruido == 0: return 1.0
               
        return 1 - np.tanh(abs(np.polyfit(np.arange(len(tramo)), tramo, 1)[0] / ruido))

    def transpMutProb(self, firstTranspGen=Consts.FIRST_TRANSPOSON_GENERATION, rangeLength=25):
        """
        Calculates the probability of transposon mutation based on the trend.
        
        :param firstTranspGen: The first generation that will include transposons.
        :param rangeLength: The number of generations from the most recent ones, that shall be considered for calculating the probability
        :return: The probability of transposon mutation based on the trend.
        """
        L = len(self.meanScores)
        if L < firstTranspGen: return 0.0
        stagnation = self.getStagnationRatio(L-min(rangeLength,L), L-1)
        return stagnation*Consts.MAX_PROB_TRANSPOSON_MUTATION if stagnation >= 0.4 else 0.0 #* Consts.MAX_PROB_TRANSPOSON_MUTATION

    def transposonMutation(self):
        if Consts.USE_TRANSPOSONS:
            prob = self.transpMutProb()
            for snake in self.snakes:
                genes = snake.DNA.genes
                for transposon in snake.DNA.transposons:
                    if random.random() < prob:
                        gene = None
                        while gene is None or gene.transposon is not None: gene = genes[random.randint(0,max(len(genes)-4,0))]
                        transposon.migrate(gene,snake.DNA)

                for i in range(Consts.SNAKE_INPUTS+1):
                    genes[i].newLayer = (i % Consts.SNAKE_INPUTS) == 0
                    genes[i].isExpressed = True

    def mutation(self):
        for snake in self.snakes:
            for layer in snake.brain:
                for neuron in layer:
                    for i in range(len(neuron)):
                        if random.random() < Consts.PROB_MUTATION: neuron[i] = Utils.random_unbounded_float()

    def displayGenData(self,newBestSnake,generation,display):
        if generation is not None and not display:
            pop = self.snakes[:]
            pop.sort(key=lambda snake: -snake.fitness)
            Utils.move_cursor(0,0)
            gen = Utils.getFormattedInt(generation,4)
            genMeanScore = Utils.getFormattedInt(round(self.meanScores[-1],1),3)
            bestFitness  = Utils.getFormattedInt(round(pop[0].fitness,1),3)
            newBestSnakeTag = f' | New best snake! {Utils.getFormattedInt(round(self.currBestSnake.fitness,1),4)}' if newBestSnake else ''
            print(f"Generation {gen}: Score mean -> {genMeanScore} | Best Snake -> [fitness: {bestFitness}] {newBestSnakeTag}")

    def runGeneration(self,generation=None,display=True, displayGeneration=False,bestSnakeName="BestSnake"):
        newBestSnake = self.evaluateSnakes(generation,display, displayGeneration=displayGeneration)
        self.saveCurSnakes(generation,bestSnakeName)
        self.displayGenData(newBestSnake,generation,display)
        self.crossover()
        self.transposonMutation()
        self.mutation()

        self.prevBestSnake = copy.deepcopy(self.currBestSnake)