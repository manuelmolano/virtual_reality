# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 15:00:03 2018

@author: molano
"""

import GameLogic, bge, time
def give_reward():
    #gets the current object (the empty object)
    controller = bge.logic.getCurrentController()
    keyboard = controller.sensors['water (C)']
    #the bell!
    bell = controller.actuators['bell']
    if keyboard.status==1:
        goal_word = 'FREEGOAL' 
        # play the bell
        bell.startSound()
            
        if GameLogic.globalDict['pump_control']:
            GameLogic.globalDict['ser'].write(goal_word)   
            # I send the command 'run\r\n' to the PUMP
            word = 'run\r\n'
            GameLogic.globalDict['PUMP'].write(word)
    elif keyboard.status==3:
        if GameLogic.globalDict['pump_control']:
            # I send the command 'run\r\n' to the PUMP
            word = 'stp\r\n'
            GameLogic.globalDict['PUMP'].write(word)        
        
        
def query_pump():
    #gets the current object (the empty object)
    controller = bge.logic.getCurrentController()
    keyboard = controller.sensors['query pump (J)']
    if keyboard.status==1: 
        if GameLogic.globalDict['pump_control']:
            # I send the command 'run\r\n' to the PUMP
            word = 'rat\r\n'
            GameLogic.globalDict['PUMP'].write(word)
            print('pressed')
    elif keyboard.status==3:
        if GameLogic.globalDict['pump_control']:
            print('released')
            print(GameLogic.globalDict['PUMP'].read(GameLogic.globalDict['PUMP'].inWaiting()))        
    
    
    
    
def move_keyboard():
    movSpeed = 0.5
    rotSpeed = 0.01
    cont = bge.logic.getCurrentController()
    player = cont.owner
    # I need to control the radars
    rf = cont.sensors['Radar_front']
    keyboard = bge.logic.keyboard
    if bge.logic.KX_INPUT_ACTIVE == keyboard.events[bge.events.UPARROWKEY]:    
        if not rf.positive:
            # if the radar do no detect anything, a apply the mvement
            player.applyMovement([0,movSpeed,0],True)
    if bge.logic.KX_INPUT_ACTIVE == keyboard.events[bge.events.DOWNARROWKEY]:
        player.applyMovement([0,-movSpeed,0],True)
    if bge.logic.KX_INPUT_ACTIVE == keyboard.events[bge.events.LEFTARROWKEY]:
        player.applyRotation([0,0,rotSpeed],True)
    if bge.logic.KX_INPUT_ACTIVE == keyboard.events[bge.events.RIGHTARROWKEY]:
        player.applyRotation([0,0,-rotSpeed],True)
    

def give_reward_dose():
    tiempo = time.clock() - GameLogic.globalDict['tiempo0']
    # get the beep actuator
    #beep = controller.actuators['beep']
    # play the beep
    #beep.startSound()
    # update the last reward time
    GameLogic.globalDict['tiempoLastReward'] = tiempo
   #put the word 
    goal_word = 'FREEGOAL'
    # and send it to simulink
            
    if GameLogic.globalDict['pump_control']:
        GameLogic.globalDict['ser'].write(goal_word)     
        # I send the command 'run\r\n' to the PUMP
        word = 'run\r\n'
        GameLogic.globalDict['PUMP'].write(word) 
        GameLogic.globalDict['reward'] = 1


def passive_stim():
    if  GameLogic.globalDict['timeOutReinforcement'] or GameLogic.globalDict['timeOut'] or GameLogic.globalDict['timeOutExpectation']:
        GameLogic.globalDict['passive_trials'] = 1
        print('passive stimulation!')
        
        
def finish_standby_period():
    print('End of standby period')
    cont = bge.logic.getCurrentController()
    own = cont.owner
    own['endStandbyPeriod'] = 1
        
        
        