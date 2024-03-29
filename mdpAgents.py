# mapAgents.py
# parsons/11-nov-2017
#
# Version 1.0
#
# A simple map-building to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is an extension of the above code written by Simon
# Parsons, based on the code in pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys

#
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
#
class Grid:
         
    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print
        
    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

#
# An agent that creates a map.
#
# As currently implemented, the map places a % for each section of
# wall, a * where there is food, and a space character otherwise. That
# makes the display look nice. Other values will probably work better
# for decision making.
#
class MDPAgent(Agent):

    # The constructor. We don't use this to create the map because it
    # doesn't have access to state information.
    def __init__(self):
        print "Running init!"

    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent.
    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.addWallsToMap(state)
         self.updateFoodInMap(state)
         self.map.display()
         #Run the value iteration 1000 times at the start as it will stabilise the values for later on
         self.updateUtilities(api.walls(state), api.food(state), api.ghosts(state), 1000, state)
         self.counter = 0
       


    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"
        self.counter = 0

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)
        
    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map and set the value to -5
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], -5)

    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        # Set the blank spaces to -3 and walls are set to -5
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != -5:
                    self.map.setValue(i, j, -3)
        
        #Get the food and for each food coordinate, add it to the map and set the value to 10
        food = api.food(state)    
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], 10)
        

    #This is the main method which applies value iteration and can be thought of as the MDP Solver
    # @param self : passed implicitly, used to call functions within the object
    # @param walls: walls array
    # @param food : food array in the current state
    # @param ghosts : ghost array in the current state
    # @param num : number of times value iteration must be run - Value iteration will always be run num + 1 times
    # @param state : current state
     
    def updateUtilities(self, walls, food, ghosts,num, state):

        # Outer most loop which decides how many times value iteration must be run
        for i in range(0,num):

            #gemma value to feed into bellman equation
            gemma = 0.1
            
            #Iterate over the map and get each square which isnt a wall, wall is represented as -5
            for i in range(self.map.getWidth()):
                for j in range(self.map.getHeight()):
                    #get the current value
                    current = self.map.getValue(i, j)
                    #check that its not a wall
                    if current != -5:
                        # Look at all neighbouring states which the pacman can go to 
                        north1 = (i, j+1)
                        south1 = (i, j-1)
                        east = (i+1, j)
                        west = (i-1, j)


                        #A list to keep all neighbouring states
                        coordinatesForNeighbourStates = []
                      
                        # A map to check which neighbours are the walls
                        wallMap = dict()

                    
                        # A list to store the values of all possible outcomes and for bellman to pick the maximum value from this list
                        values = []

                        # Add all neighbours to the list
                        coordinatesForNeighbourStates.append(north1)
                        coordinatesForNeighbourStates.append(south1)
                        coordinatesForNeighbourStates.append(east)
                        coordinatesForNeighbourStates.append(west)


                        #Set which of the neighbors are walls and which ones are actually squares - Simple boolean representation
                        # True means a neighbor is a wall and False means its not a wall
                        for coord in coordinatesForNeighbourStates:
                            if coord in walls:
                                wallMap[coord] = True
                            else:
                                wallMap[coord] = False

                          
                        #Iterate over all neighbors
                        for val in coordinatesForNeighbourStates:
                            #Check that the neighbour is not a wall and it is within the grid
                            if val not in walls and val[0] < self.map.getWidth() and val[1] < self.map.getHeight():
                                
                                #Initialise the probabbilities for ending up in neighbouring state
                                pNorth = 0.1
                                pSouth = 0.1
                                pEast = 0.1
                                pWest = 0.1

                                #Compute for each of the neighburing state, the maximum expected utility,
                                # as with a wall it will end up in the current state, otherwise take the value from the neighbour state
                                # Do this for all neighbours (except walls) 
                                if wallMap[north1] == True:
                                    pNorth = 0.1 * self.map.getValue(val[0], val[1])
                                else:
                                    pNorth = 0.1 * self.map.getValue(north1[0], north1[1]) 

                                if wallMap[south1] == True:
                                    pSouth = 0.1 * self.map.getValue(val[0], val[1])
                                else:
                                    pSouth =  0.1 * self.map.getValue(south1[0], south1[1])

                                if wallMap[east] == True:
                                    pEast = 0.1 * self.map.getValue(val[0], val[1])
                                else:
                                    pEast = 0.1 * self.map.getValue(east[0],east[1])

                                if wallMap[west] == True:
                                    pWest = 0.1 * self.map.getValue(val[0], val[1])
                                else:
                                    pWest = 0.1 * self.map.getValue(west[0], west[1])

                                #Compute the MEU for a move which is whether west or east, as it can end up in south or north with a probability of 0.1
                                if val == west or val == east:
                                    temp =  0.8 * self.map.getValue(val[0], val[1]) + pSouth + pNorth
                                    values.append(temp)
                                #Compute the EU for north or south move, it can end up in east or south and the case if east/west is a wall it will end up in the same state
                                if val == north1 or val == south1:
                                    temp =  0.8 * self.map.getValue(val[0],val[1]) + pEast + pWest 
                                    values.append(temp)
                                            
                        
                             
                        #Get the maximum value from the above computed values                     
                        m = max(values)

                        #Get the right hand side of bellman 
                        rightBellman = gemma * m;

                        #initiate the reward to -0.1
                        reward = -0.1
                        #Decide what the reward will be based on whether there is Food/ghosts in that square. 
                        # Its kept in mind that neighbours of the ghost state are as deadly as the ghost state itself
                        # since ghosts move and they will be in one of its  neighbour states next, hence pacman should avoid 
                        # not just ghost squares but its neighbours too. 

                        #Check that the the current sqaure has food and does not have the reward already
                        if (i,j) in food and self.map.getValue(i,j) != 10:
                            reward = 10

                        #Check that the current square or any of its neighbours do not hace a ghosts in it
                        if (i,j) in ghosts or (i+1,j) in ghosts or (i-1,j) in ghosts or (i, j+1) in ghosts or (i,j-1) in ghosts or (i+1, j+1) in ghosts or (i+1, j-1) in ghosts or (i-1, j+1) in ghosts or (i-1, j-1) in ghosts:    
                            # When the food is low and ghosts are near the food then all neighbours cannot be negatives rewards
                            if (len(food) > 2):
                                reward = -10
                            else:
                                #Food is low and ghost should be avoided but food should be eaten hence only consider adjacent neighbours
                                if (i,j) in ghosts or (i+1,j) in ghosts or (i-1,j) in ghosts or (i, j+1) in ghosts or (i,j-1) in ghosts:
                                    # set the reward to -10
                                    reward = -10   

                                                            
                        #final bellman value      
                        bellman = reward + rightBellman  

                        #set the sqaure value to the bellman value
                        self.map.setValue(i,j,bellman)    


    # A utility method which decides how many times value iteration must be called based on the amount of food remaining in the grid
    # The less the food, the more number of times it will take to get a good policy (in restricted time)
    def valueIteration(self, walls, food, ghostArray, state):
        if (len(food) < 3):
            self.updateUtilities(walls, food, ghostArray, 100, state)
        else:
            self.updateUtilities(walls, food, ghostArray, 50, state)


    # The function which calculates the next move by applying MEU formula on the current sqaure to find the best move
    # It follows the same structure as updateUtilities function
    # @returns a direction, ie Directions.West

    def getNextMoveBasedOnMEU(self, state):

        #Initialise all varibles with data from the api
        walls = api.walls(state)
        legal = api.legalActions(state)
        pacman = api.whereAmI(state)
        west = Directions.WEST
        east = Directions.EAST
        south = Directions.SOUTH
        north = Directions.NORTH
        ghostArray = api.ghosts(state)
        food = api.food(state)


        # Initialise all the lists and maps
        coordinatesForLegalMoves = []
        mapOfLegalCoordinatesToDirection = dict()
        coordinatesForNeighbourStates = []
        directionToCoordinateMap = dict()
        wallMap = dict()

        #Remove STOP move from legal if it exists
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        #Find the coordinates for neighbour states of pacman - they all represent a potential move 
        westCoord = (pacman[0]-1, pacman[1])
        eastCoord = (pacman[0]+1, pacman[1])  
        northCoord =  (pacman[0], pacman[1]+1)
        southCoord = (pacman[0], pacman[1]-1)

        #reset the value of the map of pacman's position since pacman visisted the state
        self.map.setValue(pacman[0],pacman[1], 1)

        #Iterate over the legal moves and update the maps to have a representation of the neighbour states in maps
        for l in legal:
            #check for each possible move and update the map accordingly
            if l == west:
                coordinatesForLegalMoves.append(westCoord)
                mapOfLegalCoordinatesToDirection[westCoord] = west
                directionToCoordinateMap[west] = westCoord
            if l == east:
                coordinatesForLegalMoves.append(eastCoord) 
                mapOfLegalCoordinatesToDirection[eastCoord] = east
                directionToCoordinateMap[east] = eastCoord
            if l == north:
                coordinatesForLegalMoves.append(northCoord)
                mapOfLegalCoordinatesToDirection[northCoord] = north
                directionToCoordinateMap[north] = northCoord
            if l == south:
                coordinatesForLegalMoves.append(southCoord)
                mapOfLegalCoordinatesToDirection[southCoord] = south
                directionToCoordinateMap[south] = southCoord          


        values = []

        #Add all neighbours to the list
        coordinatesForNeighbourStates.append(northCoord)
        coordinatesForNeighbourStates.append(southCoord)
        coordinatesForNeighbourStates.append(eastCoord)
        coordinatesForNeighbourStates.append(westCoord)

        #check which of the neighbour is a wall and set the boolean value in the map accordingly
        for neighbour in coordinatesForNeighbourStates:
            if neighbour in walls:
                wallMap[neighbour] = True
            else:
                wallMap[neighbour] = False
 
        # for every neighbour check that its not a wall and its within the grid
        for val in coordinatesForNeighbourStates:
            if val not in walls and val[0] < self.map.getWidth() and val[1] < self.map.getHeight():
                #initialise the probabilities
                pNorth = 0.1
                pSouth = 0.1
                pEast = 0.1
                pWest = 0.1

                #calculate the expected utility based on whether its a wall or not
                if wallMap[northCoord] == True:
                    pNorth = 0.1 * self.map.getValue(val[0], val[1])
                else:
                    pNorth = 0.1 * self.map.getValue(northCoord[0], northCoord[1]) 

                if wallMap[southCoord] == True:
                    pSouth = 0.1 * self.map.getValue(val[0], val[1])
                else:
                    pSouth =  0.1 * self.map.getValue(southCoord[0], southCoord[1])

                if wallMap[eastCoord] == True:
                    pEast = 0.1 * self.map.getValue(val[0], val[1])
                else:
                    pEast = 0.1 * self.map.getValue(eastCoord[0],eastCoord[1])

                if wallMap[westCoord] == True:
                    pWest = 0.1 * self.map.getValue(val[0], val[1])
                else:
                    pWest = 0.1 * self.map.getValue(westCoord[0], westCoord[1])

                #for each possible move, calculate the expected utility
                if val == westCoord:
                    temp =  0.8 * self.map.getValue(val[0], val[1]) + pNorth + pSouth
                    values.append((temp, west))
                if val == eastCoord:
                    temp =  0.8 * self.map.getValue(val[0], val[1]) + pNorth + pSouth 
                    values.append( (temp,east ) )
                if val == northCoord:
                    temp =  0.8 * self.map.getValue(val[0],val[1]) + pEast + pWest 
                    values.append((temp, north))
                if val == southCoord:
                    temp =  0.8 * self.map.getValue(val[0],val[1]) + pEast + pWest 
                    values.append((temp, south))
                            
        

        #initialisation of variables to record the maximum value and move 
        maximum = -10
        moveToMake = random.choice(legal)
      
        # Find the maximum value from the list of expected utilities
        for m in values:
            if m[0] > maximum:
                maximum = m[0]
                moveToMake = m[1]


        #check with the map that the move calculated will not kill pacman and if it wont then proceed with returning it
        deathMove = False
        for g in ghostArray:
            if directionToCoordinateMap[moveToMake] == g:
                deathMove = True
    
        if deathMove == False:
            direction = moveToMake
        else:
            if (len(legal) > 1):
                legal.remove(moveToMake);
                direction = random.choice(legal)
            else:
                direction = moveToMake

        #return the best direction
        return direction
    
    def getAction(self, state):
        
        #Initialise all variables
        walls = api.walls(state)
        ghostArray = api.ghosts(state)
        food = api.food(state)
        legal = api.legalActions(state)
        
        #Run value iteration and update the map
        self.valueIteration(walls, food, ghostArray, state)

        #Get the direction based on MEU 
        direction = self.getNextMoveBasedOnMEU(state)


        #return with a move
        return api.makeMove(direction, legal)



   
