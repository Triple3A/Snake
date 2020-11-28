#!/usr/bin/env python
# coding: utf-8

# # پروژه اول
# ### هدف از این پروژه آشنایی با الگوریتم‌های ناآگاهانه و آگاهانهٔ سرچ است

# In[71]:


import time
import sys
import numpy as np
from heapq import heappush
from heapq import heappop


# In[72]:


def tupleAdd(head, action):
    global XMAP, YMAP
    x, y = head
    deltaX, deltaY = action
    return ((x + deltaX) % XMAP, (y + deltaY) % YMAP)
    
    
def isSeed(head, seeds):
    return True if seeds.get(head, 0) > 0 else False


def distance(point1, point2):
    x, y = point1
    a, b = point2
    deltaX = min((-1 * abs(x - a)) % XMAP, abs(x - a))
    deltaY = min((-1 * abs(y - b)) % YMAP, abs(y - b))
    return deltaX + deltaY


# In[73]:


class Snake():
    def __init__(self, x, y):
        self.head = (x, y)
        self.body = [(x, y)]
        self.ate = False
    
    def canMove(self, action):
        newHead = tupleAdd(self.head, action)
        if len(self.body) > 2:
            for body in self.body[1:]:
                if newHead == body:
                    return False
        else:
            if newHead == self.body[0]:
                return False
            
        return True
    
    def copy(self):
        x, y = self.head
        copySnake = Snake(x, y)
        copySnake.body = self.body.copy()
        copySnake.ate = self.ate
        return copySnake
    
    def move(self, action):
        newHead = tupleAdd(self.head, action)
        self.head = newHead
        self.body.append(self.head)
        if self.ate:
            self.ate = False
        else:
            self.body.pop(0)
    
    def eatSeed(self, seeds):
        seeds[self.head] -= 1
        self.ate = True


# # پیاده سازی مار
# 
# برای پیاده سازی مار, کلاسی ساخته‌ایم که قسمت سر, بدن و همینطور مقداری برای اینکه مشخص کند آیا در حرکت قبلی دانه‌ای را خورده‌است یا خیر
# 
# همچنین تابع‌هایی برای حرکت و خوردن دانه نیز طراحی شده‌اند
# 

# In[74]:


class State():
    def __init__(self, snake, seeds):
        self.snake = snake
        self.seeds = seeds
        self.parent = None
        self.side = None
        self.level = 0
        
#     def copy(self):
#         return State(self.snake, self.seeds)
    
    def child(self, action):
        if self.snake.canMove(action):
            copySnake = self.snake.copy()
            copySeeds = self.seeds.copy()
            copySnake.move(action)
            
            if isSeed(copySnake.head, copySeeds):
                copySnake.eatSeed(copySeeds)
            return State(copySnake, copySeeds)
        else:
            return None
    
    def __eq__(self, other):
        if other is None:
            return False
        if self.snake.head == other.snake.head:
            if self.snake.body == other.snake.body:
                if self.seeds == other.seeds:
                    return True
        return False
    
    def __lt__(self, other):
        return True
    
    def __hash__(self):
        return hash((tuple(self.snake.body), tuple(self.seeds)))
    
        
    def distanceHeuristic(self):
        minDistance = sys.maxsize
        for loc in self.seeds.keys():
            dist = distance(self.snake.head, loc)
            if dist < minDistance:
                minDistance = dist
        return minDistance

    def heuristic(self):
        return len(self.seeds)


# # پیاده سازی استیت ها
# 
# برای هر استیت, مار و دانه‌ها و همینطور پدر و جهتی که به این استیت وارد شده‌ایم را ذخیره می‌کنیم
# با هر action اگر میشد به استیتی برویم٫ آن استیت را به عنوان فرزند برمی‌گردانیم
# 
# ### دو تابع heuristic به صورت هستند:
# 1. تعداد دانه‌های باقی‌مانده در هر استیت را درنظر می‌گیرد. این تابع هم admissible است و هم consistent. زیرا تعداد دانه های باقی مانده در هر استیت برابر تعداد دانه های هر استیت است(admissible). همینطور با هر حرکت حداکثر یک دانه خورده می‌شود و به path cost یک واحد اضافه می‌شود. بنابراین در کل تابع f_state صعودی خواهد بود.
# 
# 
# 2. حداقل تعداد حرکت های لازم تا نزدیک ترین دانه. این تابع نیز admissible است زیرا تعداد حرکت ها برای رسیدن به نزدیک ترین دانه همواره از حداقل آن کمتر است. این تابع نسبت به تابع قبلی عملکرد بهتری دارد زیرا محدودیت‌های بیشتری را درنظر گرفته است.
# 

# In[75]:


class Problem():
    def __init__(self):
        self.seeds = {}
        
        
    def getInput(self, fileName):
        f = open(fileName, 'r')
        global XMAP, YMAP
        XMAP, YMAP = map(int, f.readline().split(','))
        xSnake, ySnake = map(int, f.readline().split(','))
        self.snake = Snake(xSnake, ySnake)
        f.readline()
        for line in f:
            x, y, score = map(int, line.split(','))
            self.seeds[(x, y)] = score

        self.initState = State(self.snake, self.seeds)
        self.nowState = self.initState

        f.close()
            
        
    def goalTest(self, state):
        seeds = state.seeds
        for loc, score in seeds.items():
            if score > 0:
                return False
        return True
    
    
    def actions(self):
        ACTIONS = {'left': (0, -1), 'right': (0, 1), 'up': (-1, 0), 'down': (1, 0)}
        children = []
        
        for side, action in ACTIONS.items():
            nextState = self.nowState.child(action)
            if nextState != None:
                children.append((side, nextState))
        
        return children
    
    def findWay(self, lastChild):
        child = lastChild
        solution = []
        while(child.parent != None):
            solution.append(child.side)
            child = child.parent
        solution.reverse()
        return solution
        
        
    def bfsSolution(self):
        numStates = 1
        repeatedStates = 0
        queue = [self.initState]
        explored = {self.initState}
        if self.goalTest(self.initState):
            return (self.findWay(state), numStates, numStates - repeatedStates)
        
        while(len(queue) != 0):
            self.nowState = queue.pop(0)
            for action in self.actions():
                side, state = action
                numStates += 1
                if state not in explored:
                    explored.add(state)
                    state.parent = self.nowState
                    state.side = side
                    queue.append(state)
                    if self.goalTest(state):
                        return (self.findWay(state), numStates, numStates - repeatedStates)
                else:
                    repeatedStates += 1
        return False
        
        
    def idsSolution(self):
        i = 0
        repeatedStates = []
        numStates = [1]
        while(True):
            distance = {self.initState: 0}
            lastChild = self.dfs(self.initState, 0, i, distance, numStates, repeatedStates)
            if lastChild == None:
                i += 1
            else:
                return (self.findWay(lastChild), len(numStates), len(numStates) - len(repeatedStates))
        
        
    def dfs(self, initState, depth, maxDepth, distance, numStates, repeatedStates):
        if depth == maxDepth:
            if self.goalTest(initState):
                return initState
            else:
                return None

        self.nowState = initState
        for action in self.actions():
            side, state = action
            numStates.append(1)
            if state not in distance:
                distance[state] = distance[initState] + 1
                state.parent = initState
                state.side = side
                dfs = self.dfs(state, depth + 1, maxDepth, distance, numStates, repeatedStates)
                if dfs != None:
                    return dfs

            elif distance[state] > distance[initState] + 1:
                repeatedStates.append(1)
                distance[state] = distance[initState] + 1
                state.parent = initState
                state.side = side
                dfs = self.dfs(state, depth + 1, maxDepth, distance, numStates, repeatedStates)
                
                if dfs != None:
                    return dfs
            else:
                repeatedStates.append(1)

        return None

    
    
            
    def consistentAStar(self):
        numStates = 1
        repeatedStates = 0
        frontier = []
        heappush(frontier, (self.initState.level + self.initState.heuristic(), self.initState))
        explored = {self.initState}
        if self.goalTest(self.initState):
            return (self.findWay(self.initState), numStates, numStates - repeatedStates)
        
        while(len(frontier) != 0):
            f, self.nowState = heappop(frontier)
            for action in self.actions():
                numStates += 1
                side, state = action
                if state not in explored:
                    explored.add(state)
                    state.level = self.nowState.level + 1
                    state.parent = self.nowState
                    state.side = side
                    f_state = state.level + state.heuristic()
                    value = (f_state, state)
                    heappush(frontier, value)
                    if self.goalTest(state):
                        return (self.findWay(state), numStates, numStates - repeatedStates)
                else:
                    repeatedStates += 1
                    
        return False
        
        
    def admissibleAStar(self):
        numStates = 1
        repeatedStates = 0
        frontier = []
        heappush(frontier, (self.initState.distanceHeuristic(), self.initState))

        explored = {self.initState}
        if self.goalTest(self.initState):
            return (self.findWay(self.initState), numStates, numStates - repeatedStates)
        
        while(len(frontier) != 0):
            f, self.nowState = heappop(frontier)
            for action in self.actions():
                numStates += 1
                side, state = action
                if state not in explored:
                    explored.add(state)
                    state.level = self.nowState.level + 1
                    state.parent = self.nowState
                    state.side = side
                    heappush(frontier, (state.level + state.distanceHeuristic(), state))
                    if self.goalTest(state):
                        return (self.findWay(state), numStates, numStates - repeatedStates)
                else:
                    repeatedStates += 1
                    
        return False
    
    
    def weightedAStar(self, alpha):
        numStates = 1
        repeatedStates = 0
        frontier = []
        heappush(frontier, (self.initState.distanceHeuristic() * alpha, self.initState))

        explored = {self.initState}
        if self.goalTest(self.initState):
            return (self.findWay(self.initState), numStates, numStates - repeatedStates)
        
        while(len(frontier) != 0):
            f, self.nowState = heappop(frontier)
            for action in self.actions():
                numStates += 1
                side, state = action
                if state not in explored:
                    explored.add(state)
                    state.level = self.nowState.level + 1
                    state.parent = self.nowState
                    state.side = side
                    heappush(frontier, (state.level + state.distanceHeuristic() * alpha, state))
                    if self.goalTest(state):
                        return (self.findWay(state), numStates, numStates - repeatedStates)
                else:
                    repeatedStates += 1
                    
        return False


# #### برای سوال یک کلاس درنظر گرفته شده است که استیت کنونی و همینطور استیت شروع را ذخیره می کند.
# تابع action به این صورت پیاده سازی شده‌است که فرزندان استیت کنونی(فرزندانی که مجاز هستند) را در یک لیست برمی گرداند
# 
# تابع goalTest به این صورت عمل می‌کند که آیا مقدار همه دانه‌ها صفر شده‌است یا خیر. به عبارت دیگه آیا تمام دانه‌ها خورده شده‌اند یا خیر.
# 
# ### الگوریتم bfs:
# این الگوریتم اپتیمال است و نسبت به الگوریتم ناآگانه ids کمی سریعتر است. این الگوریتم در هر مرحله استیتی که در سر صف وجود دارد را خارج می‌کند و استیت‌های فرزندش را در صورتی که دیده نشده باشند وارد صف می کند. این الگوریتم تا زمانی ادامه پیدا می‌کند که یا استیت نهایی دیده شود و یا صف خالی شود.
# 
# ### الگوریتم ids:
# این الگوریتم نیز اپتیمال است. در هر مرحله به ازای عمق های مختلف از ۰ تا بی نهایت الگوریتم dfs رااجرا می کند. بنابراین این الگوریتم با اینکه از لحاظ اوردر زمانی مانند الگوریتم bfs است ولی تفاوت زمانی قابل ملاحظه ای دارد.
# 
# ### الگوریتم*A:
# این الگوریتم تقریبا مانند bfs عمل می‌کند با این تفاوت که در هر مرحله از بین استیت‌های قابل expand یا frontier استیتی را انتخاب می‌کند که کمترین مقدار تابع مشخص شده را داشته باشد.
# 
# f_state = path cost + heuristic
# 
# ### الگوریتم *weighted A:
# این الگوریتم تنها تفاوتی که با الگوریتم *A دارد, ضریب دادن به تابع heuristic است. هرچه تابع heuristic بهتر انتخاب شده باشد, عملکرد این الگوریتم بهتر است زیرا وزن تابع heuristic بیشتر می‌شود. (ضریب بزرگتر از ۱)
#  
# f_state = path cost + heuristic * alpha

# In[76]:


XMAP = 0
YMAP = 0
fileName = './tests/test1.txt'
p = Problem()
p.getInput(fileName)


# In[77]:


#BFS
tic1 = time.time()
bfsSolution, numStates, uniqueStates = p.bfsSolution()
toc1 = time.time()
print(numStates, uniqueStates)
print(bfsSolution)
print((toc1 - tic1))


# In[78]:


#IDS
tic2 = time.time()
idsSolution, numStates, uniqueStates = p.idsSolution()
toc2 = time.time()
print(numStates, uniqueStates)
print(idsSolution)
print(toc2 - tic2)


# In[79]:


#Admissible and Consistent Heuristic: number of seeds
tic3 = time.time()
consistentAStarSol, numStates, uniqueStates = p.consistentAStar()
toc3 = time.time()
print(numStates, uniqueStates)
print(consistentAStarSol)
print(toc3 - tic3)


# In[80]:


#Admissible Heuristic: distance
tic4 = time.time()
admissibleAStarSol, numStates, uniqueStates = p.admissibleAStar()
toc4 = time.time()
print(numStates, uniqueStates)
print(admissibleAStarSol)
print(toc4 - tic4)


# In[81]:


#Weighted A*: alpha = 1.9
tic5 = time.time()
weighted2AStarSol, numStates, uniqueStates = p.weightedAStar(1.9)
toc5 = time.time()
print(numStates, uniqueStates)
print(weighted2AStarSol)
print(toc5 - tic5)


# In[82]:


#Weighted A*: alpha = 4
tic6 = time.time()
weighted5AStarSol, numStates, uniqueStates = p.weightedAStar(4)
toc6 = time.time()
print(numStates, uniqueStates)
print(weighted5AStarSol)
print(toc6 - tic6)


# ## تست ۱
# | |زمان اجرا  | تعداد استیت مجزای دیده شده | تعداد استیت دیده شده | مسیر جواب | فاصله جواب | الگوریتم |
# |:-:| :-: | :-: | :-: | :-: | :-: | :-: |
# ||0.1345|4469 | 8984|LDLURDLUULUL |12 | BFS|
# ||0.750 |13350 | 40613| LDLURDLUULUL| 12| IDS|
# ||0.159 |3876 |7430 | DLDLURULUULL| 12| *seedsA |
# ||0.104  |2556 |4473 | DLRULDLUUULL|12 | *distanceA |
# ||0.1075 |2407 |4208 |DLLURDLUUULL |12 | alpha = 1.9 |
# || 0.085|1003 |1613 |DLULDRUULLUL | 12| alpha = 4|
# 

# ## تست ۲
# | |زمان اجرا  | تعداد استیت مجزای دیده شده | تعداد استیت دیده شده | مسیر جواب | فاصله جواب | الگوریتم |
# |:-:| :-: | :-: | :-: | :-: | :-: | :-: |
# ||1.6725|45695 | 101208|LRRULLLUUULLLLU |15 | BFS|
# ||9.885 |162338 | 512422| LRRULLLUUULLLLU| 15| IDS|
# ||2.376 |50390 |109736 | RULDLUULUULULLL| 15| *seedsA |
# ||1.808  |28929 |59923 | RLLURUULULLULLL|15 | *distanceA |
# ||1.3725 |26030 |53816 |RULDLUULUULLLUL |15 | alpha = 1.9 |
# || 0.695|15478 |30663 |RLLURULULULULLL | 15| alpha = 4|
# 
# 

# ## تست ۳
# | |زمان اجرا  | تعداد استیت مجزای دیده شده | تعداد استیت دیده شده | مسیر جواب | فاصله جواب | الگوریتم |
# |:-:| :-: | :-: | :-: | :-: | :-: | :-: |
# ||12.998|218024 | 491261|RURDDDRRDRRRDDRRULLDLLLUU |25 | BFS|
# ||111.244 |862090 | 3871636| RURDDDRRDRRRDDRRULLDLLLUU| 25| IDS|
# ||10.872 |192682 |420052 | URDDDRRRDDRRRDRRULLDLUULL| 25| *seedsA |
# ||8.232  |137022 |296893 | URDDDRRDRRRDDRURRDLLLLUUL|25 | *distanceA |
# ||7.205 |126465 |274172 |URDRDDDRRDRRDRURRDLLLUULL |25 | alpha = 1.9 |
# || 2.8095|53718 |106765 |URRDDDRDRULDRDRDRRRRRULLLD | 26| alpha = 4|
# 
# 
# 
