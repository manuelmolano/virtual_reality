# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 18:53:41 2017

@author: molano
"""

import  GameLogic, random
import ops
def next_trial(scene,num_trials,own,tiempo,starting_ori):
    if GameLogic.globalDict['circle_counter']<num_trials and GameLogic.globalDict['triangle_counter']<num_trials:
        put_the_door(scene,tiempo)
    elif GameLogic.globalDict['circle_counter']==num_trials and GameLogic.globalDict['triangle_counter']==num_trials:
        #this is the end of the passive stimulation. From here we go to the black wall after the reinforcement periods
        own.position[1] = starting_ori.position[1]
        ops.display_blackScreen(scene,own,tiempo)
        GameLogic.globalDict['passive_trials'] = 0
        GameLogic.globalDict['passive_stim'] = 0
        GameLogic.globalDict['circle_counter'] = 0
        GameLogic.globalDict['triangle_counter'] = 0
        tiempo_string = str(tiempo)
        tiempo_string = tiempo_string[0:tiempo_string.find('.')+4]
        word = "".join(['passive_stim_end',tiempo_string,'\n'])
        GameLogic.globalDict['summary'].write(word)
    
    elif GameLogic.globalDict['circle_counter']==num_trials:
        GameLogic.globalDict['currentPassiveStim'] = scene.objects['reinforcementWallTriangle']
        GameLogic.globalDict['currentPassiveStim'].position[0] = -70
        GameLogic.globalDict['currentPassiveStim'].position[1] = 124.06228
        GameLogic.globalDict['currentPassiveStim'].position[2] = 17
        GameLogic.globalDict['passive_stim'] = 1
        GameLogic.globalDict['triangle_counter'] +=1
        #write to file
        tiempo_string = str(tiempo)
        tiempo_string = tiempo_string[0:tiempo_string.find('.')+4]
        word = "".join(['triangle',tiempo_string,'\n'])
        GameLogic.globalDict['passive_stim_seq'].write(word) 
    elif GameLogic.globalDict['triangle_counter']==num_trials:
        GameLogic.globalDict['currentPassiveStim'] = scene.objects['reinforcementWallCircle']
        GameLogic.globalDict['currentPassiveStim'].position[0] = -70
        GameLogic.globalDict['currentPassiveStim'].position[1] = 124.06228
        GameLogic.globalDict['currentPassiveStim'].position[2] = 17
        GameLogic.globalDict['passive_stim'] = 1
        GameLogic.globalDict['circle_counter'] +=1
        #write to file
        tiempo_string = str(tiempo)
        tiempo_string = tiempo_string[0:tiempo_string.find('.')+4]
        word = "".join(['circle',tiempo_string,'\n'])
        GameLogic.globalDict['passive_stim_seq'].write(word) 
def put_the_door(scene,tiempo):
    next_stim = next_stimulus()
    if next_stim==0:
        GameLogic.globalDict['currentPassiveStim'] = scene.objects['reinforcementWallTriangle']
        GameLogic.globalDict['triangle_counter'] +=1
        shape = 'triangle'
    else:
        GameLogic.globalDict['currentPassiveStim'] = scene.objects['reinforcementWallCircle']
        GameLogic.globalDict['circle_counter'] +=1
        shape = 'circle'
    #place the reinforcement walls                     
    GameLogic.globalDict['currentPassiveStim'].position[0] = -70
    GameLogic.globalDict['currentPassiveStim'].position[1] = 124.06228
    GameLogic.globalDict['currentPassiveStim'].position[2] = 17
    GameLogic.globalDict['passive_stim'] = 1
    
    #write to file
    tiempo_string = str(tiempo)
    tiempo_string = tiempo_string[0:tiempo_string.find('.')+4]
    word = "".join([shape,tiempo_string,'\n'])
    GameLogic.globalDict['passive_stim_seq'].write(word) 


def next_stimulus():
    #we first choose the position of the reward
    #manual control
    if len(GameLogic.globalDict['stims_mat'])>=GameLogic.globalDict['numb_data_pseudoRandom_passStim']:       
        if sum(GameLogic.globalDict['stims_mat'])/len(GameLogic.globalDict['stims_mat']) ==1:
            next_stim = 0
        elif sum(GameLogic.globalDict['stims_mat'])/len(GameLogic.globalDict['stims_mat']) ==0:
            next_stim = 1
        else:
            next_stim = random.randint(0,1)
    else:
        next_stim = random.randint(0,1)
        
            
    if len(GameLogic.globalDict['stims_mat'])<GameLogic.globalDict['numb_data_pseudoRandom_passStim']:
        GameLogic.globalDict['stims_mat'].append(next_stim)
    else:
        #print(GameLogic.globalDict['stims_mat'])
        #print(GameLogic.globalDict['stims_mat'][0:GameLogic.globalDict['numb_data_pseudoRandom_passStim']])
        GameLogic.globalDict['stims_mat'][0:GameLogic.globalDict['numb_data_pseudoRandom_passStim']-1] = GameLogic.globalDict['stims_mat'][1:GameLogic.globalDict['numb_data_pseudoRandom_passStim']] 
        aux = next_stim
        GameLogic.globalDict['stims_mat'][GameLogic.globalDict['numb_data_pseudoRandom_passStim']-1] = aux    
            
   
        
        
              
    return(next_stim)        