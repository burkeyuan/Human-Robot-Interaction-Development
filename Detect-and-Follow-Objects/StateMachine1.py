#!/usr/bin/python3
import ctypes
import api
import os
import time
import sys
import struct
from pixy import *
from ctypes import *

class State:
        Idle,TurningLeft,TurningRight,MovingForward,BeginSearch,LookLeft,LookRight = range(7)

class SearchResult:
        ObjectLeft,ObjectCenter,ObjectRight,NoObject = range(4)

class Blocks (Structure):
  _fields_ = [ ("type", c_uint),
               ("signature", c_uint),
               ("x", c_uint),
               ("y", c_uint),
               ("width", c_uint),
               ("height", c_uint),
               ("angle", c_uint) ]

blocks = BlockArray(100)

#system configuration parameters
leftBound = 120
rightBound = 180

def delayMS(delayAmmount):
        time.sleep(delayAmmount/1000)

def checkObject():
        #search for objects and if there is an object
        count = pixy_get_blocks(100,blocks)
        if count > 0:
                return True
        return False

def checkLeftRightMiddle():
        #check to see if object is in left right or middle if
        count = pixy_get_blocks(100,blocks)
        maxIndex= 0 #index of maximum sized object
        max = 0
        if count == 0:
                return SearchResult.NoObject
        for index in range (0, count):
                area = blocks[index].width * blocks[index].height
                if area > max:
                        max = area
                        maxIndex = index
        print("X Reading: " + str(blocks[maxIndex].x))
        if (blocks[maxIndex].x < leftBound):
                return SearchResult.ObjectLeft
        elif (blocks[maxIndex].x < rightBound):
                return SearchResult.ObjectCenter
        else:
                return SearchResult.ObjectRight


#performs actions needed by state machine
#returns the Updated state
def ManageState(CurrentState):
        if(int(CurrentState) == State.Idle): #MOSTLY COMPLETE(add wait later)
                api.PlayAction(15)
                print('Sit');
                #delay for a set ammount of time before beginning next search
                #either use RME or delay function
                delayMS(2000)
                api.PlayAction(8)
                print('Standing to start search');
                return State.BeginSearch
        elif(int(CurrentState) == State.TurningLeft):  #INCOMPLETE (Delay Required)
                #move to the left a bit
                api.Walk(True)
                api.WalkMove(0)
                api.WalkTurn(20)
                delayMS(1000)
                print("Turn Left")
                return State.BeginSearch #for now go back to being search
        elif(int(CurrentState) == State.TurningRight): #INCOMPLETE (Delay Required)
                #move to the right a bit
                api.Walk(True)
                api.WalkMove(0)
                api.WalkTurn(-20)
                delayMS(1000)
                print("Turn Right")
                return State.BeginSearch #for now go back to being search
        elif(int(CurrentState) == State.MovingForward): #INCOMPLETE (Delay Required)
                #move forward a little bit
                print("Moving Forward")
                api.Walk(True)
                api.WalkMove(20)
                api.WalkTurn(0)
                delayMS(1000)
                print("Moving Forward")
                return State.BeginSearch #for now go back to being search
        elif(int(CurrentState) == State.BeginSearch):  #This state will cause robot to begin moving or move its head to look more   #FINISHED
                api.WalkMove(0)
                api.WalkTurn(0)
                api.Walk(False) #turn of Walking before beginning search
                #check the camera for object using search criteria
                delayMS(500)
                print("Checking Front View")
                Result = checkLeftRightMiddle()
                if Result == SearchResult.NoObject:
                        return State.LookLeft
                if Result == SearchResult.ObjectLeft:
                        return State.TurningLeft
                elif Result == SearchResult.ObjectCenter:
                        return State.MovingForward
                else:
                        return State.TurningRight

          elif(int(CurrentState) == State.LookLeft): #INCOMPLETE
                #play action where left arm raised

                #play action where head looks left
                print("Checking Left")
                api.PlayAction(44)
                #scan for objects
                objectFound = checkObject()
                #play standing action to return the head to center
                api.PlayAction(8)
                #if object found move head back and go to state turningLeft else go to LookRight
                if(objectFound):
                       return State.TurningLeft
                else:
                        return State.LookRight

          elif(int(CurrentState) == State.LookRight): #INCOMPLETE
                #play action where right arm raised

                #play action where head looks right
                print("Checking Right")
                api.PlayAction(45)
                #scan for objects
                objectFound = checkObject()
                #play standing action to return the head to center
                api.PlayAction(8)
                #if object found move head back and go to state TurningRight else go to Idle state
                if(objectFound):
                        return State.TurningRight
                else:
                        return State.Idle
        else:
                pass  #This line should never be hit
