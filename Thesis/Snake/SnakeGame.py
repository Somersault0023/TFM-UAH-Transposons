from copy import deepcopy
import math
import time
import heapq
import Utils.Constants as Consts
from Utils import Utils
from Snake.Snake import *

class SnakeGame:
    def __init__(self, width=Consts.BOARD_WIDTH, height=Consts.BOARD_HEIGHT, snake: Snake = None):
        self.width  = width
        self.height = height
        self.apple = [0,0]
        self.snake = snake if snake is not None else Snake()
        self.lastMove = "NONE"
        self.reset()

    def reset(self, snake: Snake = None):
        if snake is not None: self.snake = snake
        self.snake.reset(self.width,self.height)
        self.placeNewApple()

        self.score = 0
        self.meanStepsPerFeed = []
        self.stepsSinceLastFeed = 0

    def placeNewApple(self):
        do = True #Do while
        h = self.snake.body[0]
        while do or tuple(self.apple) in self.snake.tupleBody or (self.apple[0] == h[0] and self.apple[1] == h[1]):
            self.apple = [random.randint(0,self.width-1),random.randint(0,self.height-1)]
            do = False

    def getAStarDistance(self, snake: Snake, goal: List[int]):
        def manhattan_distance(p1, p2): return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])
        def get_neighbors(node):
            x, y = node
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            valid_neighbors = [(nx, ny) for (nx, ny) in neighbors if 0 <= nx < 20 and 0 <= ny < 20 and (nx, ny) not in snake.tupleBody]
            return valid_neighbors

        start = deepcopy(tuple(snake.body[0]))
        open_set = []
        heapq.heappush(open_set, (0, start))

        came_from = {} #in case we wanted to reconstruct the path

        g_score = {str(start): 0}
        f_score = {str(start): manhattan_distance(start, goal)}

        while open_set:
            current_f, current = heapq.heappop(open_set)
            if current == tuple(goal): return g_score[str(current)]

            for neighbor in get_neighbors(current):
                tentative_g_score = g_score[str(current)] + 1

                if neighbor not in g_score or tentative_g_score < g_score[str(neighbor)]:
                    came_from[str(neighbor)] = current
                    g_score[str(neighbor)] = tentative_g_score
                    f_score[str(neighbor)] = tentative_g_score + manhattan_distance(neighbor, goal)
                    heapq.heappush(open_set, (f_score[str(neighbor)], neighbor))

        return 999999 #in case there is no possible path to target

    def getBodyPartsDistances(self,numParts):
        if numParts >= 1:
            parts = []
            head = self.snake.body[0]
            div = len(self.snake.body)/(numParts+1)
            for i in range(1,numParts+1):
                p = self.snake.body[int(div*i)]
                parts += [p[0]-head[0],p[1]-head[1]]
            return parts
        else: return []

    def getInput(self):
        head = self.snake.body[0]

        distances = []
        #Version considering only the three directions
        for dir in Consts.Dir.DIRS:
            move = Utils.DirToMove(dir,self.snake.lastMove)
            curTile = [head[0]+move[0],head[1]+move[1]]
            aux = 1

            while tuple(curTile) not in self.snake.tupleBody and curTile[0] >= 0 and curTile[0] < self.width and curTile[1] >= 0 and curTile[1] < self.height:
                curTile = [curTile[0]+move[0],curTile[1]+move[1]]
                aux += 1
            distances.append(aux)
        
        #version considering the four directions
        """
        for move in Consts.Move.MOVES:
            curTile = [head[0]+move[0],head[1]+move[1]] 
            aux = 1

            while tuple(curTile) not in self.snake.tupleBody and curTile[0] >= 0 and curTile[0] < self.width and curTile[1] >= 0 and curTile[1] < self.height:
                curTile = [curTile[0]+move[0],curTile[1]+move[1]]
                aux += 1
            distances.append(aux) #Utils.getNearestObstacle(self.snake.body[0],self.snake.body,move)
        """

        tail   = self.snake.body[-1]
        middle = self.snake.body[len(self.snake.body) // 2]
        return [
            len(self.snake.body),                                           #snake body length
            middle[0]-head[0],middle[1]-head[1],                            #distances to middle
            tail[0]-head[0],tail[1]-head[1],                                #distances to tail
            distances[0],distances[1],distances[2], #distances[3],          #distances to closest obstacle
            self.apple[0]-head[0],self.apple[1]-head[1],                    #distances to apple -> hacerlo con a-estrella? Utils.astar(self.snake, self.apple)
            self.getAngleToApple(),                                         #relative angle to apple
        ]

    def getAngleToApple(self):
        dx = self.snake.body[0][0] - self.apple[0]
        dy = self.snake.body[0][1] - self.apple[1]
        
        # Convertir el ángulo a grados
        angle_to_apple_deg = math.degrees(math.atan2(dy, dx))
        
        # Ajustar el ángulo relativo basado en la dirección de la serpiente
        relative_angle = {
            "[0, -1]": (lambda angleApple: (angleApple-90)  if angleApple-90  > -180 else 270+angleApple), #UP
            "[1, 0]":  (lambda angleApple: (angleApple-180) if angleApple-180 > -180 else 180+angleApple), #RIGHT
            "[0, 1]":  (lambda angleApple: angleApple+90),  #DOWN
            "[-1, 0]": (lambda angleApple: angleApple)      #LEFT
        }[str(self.snake.lastMove)](angle_to_apple_deg)

        # Normalizar el ángulo para que esté en el rango de -180 a 180 grados
        return relative_angle if relative_angle < 180 else relative_angle-360
    
    def checkGameOver(self):
        h = self.snake.body[0]
        self.ownBodyDeath = tuple(h) in self.snake.tupleBody
        return self.stepsSinceLastFeed > self.width*self.height or h[0] < 0 or h[1] < 0 or h[0] >= self.width or h[1] >= self.height or self.ownBodyDeath

    def updateBoard(self,oldTail=None,curGen=None):
        if oldTail is not None: self.placeCharacter(" ",oldTail[0],oldTail[1])
        self.placeCharacter("O",self.apple[0],self.apple[1])
        self.placeCharacter("█",self.snake.body[0][0],self.snake.body[0][1])
        self.placeCharacter("█",self.snake.body[-1][0],self.snake.body[-1][1])

        Utils.move_cursor(0,self.height*2+1)
        print(f"Apples eaten: {len(self.meanStepsPerFeed)}")
        if curGen is not None: print(f"Current Generation: {curGen}")
        print(f"Latest move: {self.lastMove}")

    def placeCharacter(self,char,x,y):
        Utils.move_cursor(2*x+1,2*y+1)
        print(char, end='')

    def checkAppleEaten(self,newTail):
        h = self.snake.body[0]
        if h[0] == self.apple[0] and h[1] == self.apple[1]:
            self.meanStepsPerFeed.append(int(self.stepsSinceLastFeed))
            self.stepsSinceLastFeed = 0
            self.placeNewApple()
            self.snake.addBodyPart(newTail)

    def drawEmptyBoard(self):
        for i in range(self.height*2):
            Utils.move_cursor(0,i)
            if i % 2 == 0:
                for ii in range(self.width): print(f"{"┬" if i == 0 else "┼"}─",end="")
                print("┐" if i == 0 else "┤")
                Utils.move_cursor(0,i)
                print("┌" if i == 0 else "├",end="")
            else:
                for ii in range(self.width): print("│ ",end="")
                print("│")

        for ii in range(self.width): print("┴─",end="")
        print("┘")
        Utils.move_cursor(0,self.height*2)
        print("└",end="")

    def start(self,display=True,curGen=None,forcePlay=False):
        if self.snake.fitness == -1 or forcePlay:
            if display: Utils.clearScreen()
            if display: self.drawEmptyBoard()
            self.reset()
            if display: self.updateBoard(None,curGen)

            self.ownBodyDeath = False
            i = None
            timesAvoidedBody = 0
            auxHead = tuple(self.snake.body[0])
            while not self.checkGameOver():
                if i is not None and not self.ownBodyDeath and tuple(map(sum, zip(auxHead, self.snake.lastMove))) in self.snake.tupleBody:
                    timesAvoidedBody += 1

                tail = self.snake.body[-1]
                i = self.getInput()
                auxHead = tuple(self.snake.body[0])
                self.lastMove = self.snake.move(i)
                self.stepsSinceLastFeed += 1
                self.checkAppleEaten(tail)
                if display:
                    self.updateBoard(tail,curGen)
                    time.sleep(0.05)

            totalApples = len(self.meanStepsPerFeed)
            #mspf = sum(self.meanStepsPerFeed)/max(totalApples,1)
            
            self.snake.fitness = totalApples*Consts.POINTS_PER_APPLE + sum(self.meanStepsPerFeed)
            self.snake.applesEaten = self.meanStepsPerFeed
        self.score = self.snake.fitness
        return self.score