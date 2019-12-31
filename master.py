# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 14:59:49 2018

@author: molano
"""

import  GameLogic, sys, bge, math, time, Rasterizer, os, random, datetime#, serial
import ops, passive_trials

def initialize(own,starting_ori,scene):
    GameLogic.globalDict.clear()
    #get parameters ofr experiment
    aux = open(own['folder']+own['mouse_id']+'\\VRparams.txt', 'r');
    GameLogic.globalDict['params'] = aux.read()
    

    # Iniziation label
    own['init'] = 1
    GameLogic.globalDict['num_trials'] = float(ops.get_data_from_VRparams('num_trials'))
    print(GameLogic.globalDict['num_trials'])
    print('#####################################################')
    print('Mouse:')
    print(own['mouse_id'])
    print('Number of trials:')
    print(GameLogic.globalDict['num_trials'])
    
       
    #Rasterizer.showMouse(True)
    #put the pointer in the center of the screen
    width = Rasterizer.getWindowWidth()
    height = Rasterizer.getWindowHeight()
    Rasterizer.setMousePosition(math.floor(width/2), math.floor(height/2))
        
    #save the starting orientation and position
    starting_ori.orientation = own.orientation
    starting_ori.position = own.position        
    #control if the user wants to send commands to the PUMP 
    GameLogic.globalDict['pump_control'] = own['pump'] 
    #control if the user wants to send data through a second port
    GameLogic.globalDict['send'] = own['send_info'] 
    #control if the user wants to send commands to the airpuff device
    GameLogic.globalDict['airpuff_control'] = own['airpuff']
    #counting trials
    GameLogic.globalDict['contadorTrials'] = 0 
    # Starting point of the last trial. 
    GameLogic.globalDict['tiempoLastTrial']  = -100
    # Starting point of the last trial. 
    GameLogic.globalDict['trial_duration'] = float(ops.get_data_from_VRparams('trial_duration'))
    # distance between the mouse and the object
    GameLogic.globalDict['distance_mouse_obj'] = float(ops.get_data_from_VRparams('distance_mouse_obj'))
    #different walls  
    invariance_exp = float(ops.get_data_from_VRparams('invariance'))
    if invariance_exp:
        GameLogic.globalDict['background_walls']  = ['backgroundObject','backgroundObject_dots','backgroundObject_stripes'] 
        GameLogic.globalDict['triangleWalls'] = ['wallTriangles','wallTriangles_dots','wallTriangles_stripes']
        GameLogic.globalDict['circleWalls'] = ['wallCircles','wallCircles_dots','wallCircles_stripes']
    else:
        GameLogic.globalDict['background_walls']  = ['backgroundObject'] 
        GameLogic.globalDict['triangleWalls'] = ['wallTriangles']
        GameLogic.globalDict['circleWalls'] = ['wallCircles']
       
    #the object to be rewarded can be changed
    rewardedObject = ops.get_data_from_VRparams('rewardedObject')
    if rewardedObject=='triangle':
        GameLogic.globalDict['rewarded_objectList'] = GameLogic.globalDict['triangleWalls']
        GameLogic.globalDict['punished_objectList'] = GameLogic.globalDict['circleWalls']
        GameLogic.globalDict['reinforcementWall'] = 'reinforcementWallTriangle'
        GameLogic.globalDict['refferenceRewardLeft'] = 0
    elif rewardedObject=='circle':
        GameLogic.globalDict['rewarded_objectList'] = GameLogic.globalDict['circleWalls']
        GameLogic.globalDict['punished_objectList'] = GameLogic.globalDict['triangleWalls']
        GameLogic.globalDict['reinforcementWall'] = 'reinforcementWallCircle'
        GameLogic.globalDict['refferenceRewardLeft'] = math.pi
        
    #position of the side white walls
    GameLogic.globalDict['sideWhiteWalls_pos'] = float(ops.get_data_from_VRparams('sideWhiteWalls_pos'))
    right_whiteWall = scene.objects['WhiteWallRight']
    left_whiteWall = scene.objects['WhiteWallLeft']
    right_whiteWall.position[1] = starting_ori.position[1] + GameLogic.globalDict['sideWhiteWalls_pos']*GameLogic.globalDict['distance_mouse_obj'] - 85
    left_whiteWall.position[1] = starting_ori.position[1] + GameLogic.globalDict['sideWhiteWalls_pos']*GameLogic.globalDict['distance_mouse_obj'] - 85
        
    #place the reinforcement walls                     
    reinforcementWall = scene.objects[GameLogic.globalDict['reinforcementWall']]
    reinforcementWall.position[0] = -70
    reinforcementWall.position[1] = 124.06228
    reinforcementWall.position[2] = 17
    GameLogic.globalDict['background_object_margin'] = 6
    reinforcementWallBackground = scene.objects['reinforcementWallBackground'] 
    reinforcementWallBackground.position[0] = -53.84418
    reinforcementWallBackground.position[1] = reinforcementWall.position[1] + GameLogic.globalDict['background_object_margin']
    reinforcementWallBackground.position[2] = reinforcementWall.position[2]  
    
    # this controls how far I put the white walls 
    GameLogic.globalDict['walls_margin'] = 6
    # front wall margin
    GameLogic.globalDict['background_object_Z'] = -4
    GameLogic.globalDict['wall_Z_component'] = 10
    #this controls how much to the sides the (invisible) reward objects is placed
    GameLogic.globalDict['sideDisplacementWalls'] = float(ops.get_data_from_VRparams('sideDisplacementWalls'))
    #this controls how much to the sides the background walls objects is placed
    GameLogic.globalDict['sideDisplacementbackgroundWalls'] = 19
    # threshold for ending the trial as a fraction of the initial distance between the mouse and the front wall
    #y-threhold
    y_th = float(ops.get_data_from_VRparams('zone.depth_hit'))
    GameLogic.globalDict['y_th_hit'] = GameLogic.globalDict['distance_mouse_obj']*(1-y_th)+ starting_ori.position[1]
    y_th = float(ops.get_data_from_VRparams('zone.depth_fail'))
    GameLogic.globalDict['y_th_fail'] = GameLogic.globalDict['distance_mouse_obj']*(1-y_th)+ starting_ori.position[1]
    #x-threhold
    x_th = float(ops.get_data_from_VRparams('zone.width'))
    GameLogic.globalDict['x_th'] = x_th*GameLogic.globalDict['sideDisplacementWalls']
    #this is used to project the mouse's position along its orientation (0 means that we will just use the original position)
    GameLogic.globalDict['length_effective_position'] = 0
    #this controls how close the mouse needs to be to the front wall for the trial to be considered fail
    GameLogic.globalDict['marginFail'] = 10        
    #this is to control that we don't present to many times in a row one side
    GameLogic.globalDict['sides_mat'] = []
    GameLogic.globalDict['numb_data_pseudoRandom'] = 3
    #this will keep the measure perfomance. I will take as right trial any in which the mouse finish on the reward side, even if he doesn't get the water.
    GameLogic.globalDict['performance_history'] = []
       
    #object list 
    GameLogic.globalDict['objects_list']  = ['TriangleSphereWall']
    #flip list (every object can be presented as it is or twisted 180 degrees)
    GameLogic.globalDict['flip_list'] = [0,math.pi] 
    #Control the presentation of reward
    GameLogic.globalDict['manualControlPresentation'] = 0
    GameLogic.globalDict['LeftRight'] = 0

    #pump veolcity
    GameLogic.globalDict['pump_velocity'] = float(ops.get_data_from_VRparams('pump_rate'))
    # Time 0
    GameLogic.globalDict['tiempo0']  = time.clock()
    #experiment duration
    GameLogic.globalDict['expDuration'] = float(ops.get_data_from_VRparams('expDuration'))
    # Last reward time. Moment in which the last reward was given
    GameLogic.globalDict['tiempoLastReward']  = -100
    # Last reward time. Moment in which the last reward was given
    GameLogic.globalDict['tiempoLastPunishment'] = -100
    # last reinforcement-presentation time. Moment in which the rewarded object was presented to help association with the water.
    GameLogic.globalDict['tiempoLastReinforcement'] = -100
    # expectation presentation time.
    GameLogic.globalDict['tiempoLastExpectation'] = -100
    #duration of the expectation period
    GameLogic.globalDict['durationExpectationPeriod'] = float(ops.get_data_from_VRparams('expectationDur'))
    #probability of expectation trial
    GameLogic.globalDict['expectactionProb'] = float(ops.get_data_from_VRparams('expectationProb'))
    #this controls whether we use a spatial threshold to trigger the end of the expectation trial
    GameLogic.globalDict['spatial_threshold'] = float(ops.get_data_from_VRparams('spatial_threshold'))
    #the spatial threhold
    GameLogic.globalDict['exp_th'] = GameLogic.globalDict['distance_mouse_obj']*(1-float(ops.get_data_from_VRparams('exp_th')))+ starting_ori.position[1]                
    # Reward time. Duration of the reward.
    GameLogic.globalDict['tiempoReward'] = float(ops.get_data_from_VRparams('tiempoReward'))
    # Reward time. Duration of the reward.
    GameLogic.globalDict['afterReward_blackWall_duration'] = float(ops.get_data_from_VRparams('afterReward_blackWall_duration'))
    # Duration of the punishment.
    GameLogic.globalDict['punishment_duration'] = float(ops.get_data_from_VRparams('punishment_duration'))
    #time spent in the reinforcement corridor
    GameLogic.globalDict['time_reinforcement'] = float(ops.get_data_from_VRparams('time_reinforcement'))
    #
    GameLogic.globalDict['endOfTrialDuration'] = 1000
    #threshold for turning    
    GameLogic.globalDict['turning_angle'] = float(ops.get_data_from_VRparams('turning_angle'))                         
    # sensitiviy for turning
    GameLogic.globalDict['turnSensitivity'] = float(ops.get_data_from_VRparams('turnSensitivity'))
    # sensitivity for moving back and forward
    GameLogic.globalDict['backForwardSensitivity'] = float(ops.get_data_from_VRparams('backForwardSensitivity'))
    # This variable controls if I have given reward and I need to stop the PUMP. No reward at the begining
    GameLogic.globalDict['reward']  = 0
    # This variable controls if the game is on timeout 
    GameLogic.globalDict['timeOut'] = 0
    #this variable controls if the game is on timeout during the reinforcement
    GameLogic.globalDict['timeOutReinforcement'] = 0
    #this variable controls if the game is on timeout during the expectation control
    GameLogic.globalDict['timeOutExpectation'] = 0
    #Window to average turning
    GameLogic.globalDict['turn_history'] = [0]
    GameLogic.globalDict['backForward_history'] = [0]
    #length of the average window
    GameLogic.globalDict['average_window'] = 60
    #this is to control that we didn't close the program yet
    GameLogic.globalDict['still_open'] = 1
    now = datetime.datetime.now()
    GameLogic.globalDict['now'] = now
    #here I will save the position of the mouse at every moment. And, when close it, I will save it.
    GameLogic.globalDict['file'] = open(own['folder']+own['mouse_id']+'\\'+str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'.txt', 'w');
    GameLogic.globalDict['summary'] = open(own['folder']+own['mouse_id']+'\\'+str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'summary.txt', 'w');        
    GameLogic.globalDict['raw_velocity'] = open(own['folder']+own['mouse_id']+'\\'+str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'raw_velocity.txt', 'w');        
    GameLogic.globalDict['passive_stim_seq'] = open(own['folder']+own['mouse_id']+'\\'+str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'passive_stim.txt', 'w');        
    GameLogic.globalDict['log'] = open(own['folder']+own['mouse_id']+'\\'+own['mouse_id']+'_log.txt', 'a+');
    
    

    #PASSIVE STIM parameters
    GameLogic.globalDict['passive_trials'] = 0
    GameLogic.globalDict['circle_counter']= 0
    GameLogic.globalDict['triangle_counter']= 0
    GameLogic.globalDict['passive_stim'] = 0 
    GameLogic.globalDict['tiempoLastStim'] = -100 
    GameLogic.globalDict['tiempoLastBlackWall'] = -100
    GameLogic.globalDict['stimDuration'] = float(ops.get_data_from_VRparams('stimDuration'))
    GameLogic.globalDict['blackWallDuration'] = float(ops.get_data_from_VRparams('blackWallDuration'))
    GameLogic.globalDict['numPassiveTrials'] = float(ops.get_data_from_VRparams('numPassiveTrials'))
    GameLogic.globalDict['blackWallDurJitter'] = float(ops.get_data_from_VRparams('blackWallDurJitter'))
    aux = float(ops.get_data_from_VRparams('mousePosPassiveStim'))
    GameLogic.globalDict['mousePosPassiveStim'] = GameLogic.globalDict['distance_mouse_obj']*(1-aux)+ starting_ori.position[1]
    GameLogic.globalDict['stims_mat'] = []
    GameLogic.globalDict['numb_data_pseudoRandom_passStim'] = int(ops.get_data_from_VRparams('numb_data_pseudoRandom_passStim'))
    
    
    # create my serial ports: ser communicates with simulink and PUMP does with the PUMP
    if GameLogic.globalDict['send']:
        GameLogic.globalDict['ser']  = serial.Serial(port='\\.\COM5',baudrate=115200)
    
    if GameLogic.globalDict['pump_control']:            
        GameLogic.globalDict['PUMP']  = serial.Serial(port='\\.\COM3',baudrate=19200)
        word = 'rat ' + str(GameLogic.globalDict['pump_velocity']) + '\r\n'
        GameLogic.globalDict['PUMP'].write(word)
        #save commands sent to the pump
        GameLogic.globalDict['PUMP_commands'] = open(own['folder']+own['mouse_id']+'\\'+str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'PUMP_commands.txt', 'w');     
        word = "".join(['RAT', str(GameLogic.globalDict['pump_velocity']),'\n'])
        GameLogic.globalDict['PUMP_commands'].write(word)   
        word = 'dir_inf \n'
        GameLogic.globalDict['PUMP_commands'].write(word)
        word = '----------------------\n'
        GameLogic.globalDict['PUMP_commands'].write(word)
    if GameLogic.globalDict['airpuff_control']: 
        GameLogic.globalDict['airPuff'] = serial.Serial(port='\\.\COM6',baudrate=9600)
    # I am going to send the environment properties: maze and goal. 
    # First, I get the time (see 'goal')     
    tiempo = time.clock() - GameLogic.globalDict['tiempo0']
    GameLogic.globalDict['tiempoLastTrial'] = tiempo
    # I write on the file all the data about the experiment
    word = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    GameLogic.globalDict['log'].write(word + '\n') 
    word = 'date'+' '+str(now.day)+'_'+str(now.month)+'_'+str(now.year)+' '+str(now.hour)
    GameLogic.globalDict['log'].write(word + '\n') 
    word = 'rewarded_obj'+' '+rewardedObject
    GameLogic.globalDict['log'].write(word + '\n') 
    word = 'num_trials' +' '+ str(GameLogic.globalDict['num_trials'])
    GameLogic.globalDict['log'].write(word + '\n') 
    word = 'trial_dur' +' '+ str(GameLogic.globalDict['trial_duration'])
    GameLogic.globalDict['log'].write(word + '\n') 
    word = 'rew_duration' +' '+ str(GameLogic.globalDict['tiempoReward'])
    GameLogic.globalDict['log'].write(word + '\n') 
    word = 'punishment_duration' +' '+ str(GameLogic.globalDict['punishment_duration'])
    GameLogic.globalDict['log'].write(word + '\n') 
    word = 'turn_sens' +' '+ str(GameLogic.globalDict['turnSensitivity'])
    GameLogic.globalDict['log'].write(word + '\n')
    word = 'BF_sens' +' '+ str(GameLogic.globalDict['backForwardSensitivity'])
    GameLogic.globalDict['log'].write(word + '\n')
    GameLogic.globalDict['log'].write(word + '\n')
    word = 'protocolo' +' '+ '170312'
    GameLogic.globalDict['log'].write(word + '\n')
        
    first_time = 1
    [reward_position,background] = ops.next_reward_position()
    ops.new_trial(reward_position,own,scene,starting_ori,first_time,GameLogic.globalDict['refferenceRewardLeft'],background)


def main():
     # this controls how far I put the white walls 
    GameLogic.globalDict['walls_margin'] = 6
    scene = bge.logic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    if own['endStandbyPeriod']==1:
        own['endStandbyPeriod'] =  2
        ops.end_of_white_or_black_screen(scene)
    elif own['endStandbyPeriod']==0:
        ops.display_blackScreen(scene,own,0)
        own['endStandbyPeriod'] =  -1
    elif own['endStandbyPeriod']==2:
        run_session()
        
        
        
def run_session():
    # I need to do this to be able to import serial
    a = os.getcwd()
    sys.path.append(a + "\2.69\python\lib\site-packages")
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    #rf = cont.sensors['Radar_front']
    scene = bge.logic.getCurrentScene()
    starting_ori = scene.objects['starting_orientation']
    
    
    if not 'init' in own:
        initialize(own,starting_ori,scene)
    else: 
        # I am sending the mouse position.
        # First, I get the time (see 'goal').   
        tiempo = time.clock() - GameLogic.globalDict['tiempo0']
        tiempo_string = str(tiempo)
        tiempo_string = tiempo_string[0:tiempo_string.find('.')+4]
        
            
        # I get the position and orientation from the object and put it together with the time. 
        word = "".join(['x' , str(math.floor(own.position[0]*100))  , 'y' , str(math.floor(own.position[1]*100)) ,'t',tiempo_string,"\n",\
                        'ORIcos' , str(math.floor(own.orientation[0][1]*100)) ,'sin', str(math.floor(own.orientation[1][1]*100)),"\n"])
        if not GameLogic.globalDict['file'].closed:
            GameLogic.globalDict['file'].write(word)
        # I need to check if the serial port is open because it could be that 'finishGame' run before and close it. 
        if GameLogic.globalDict['send'] and GameLogic.globalDict['ser'].isOpen():
                GameLogic.globalDict['ser'].write(word)    
    
        #get the time that is shown in the screen
        own['time'] = round(tiempo/60)
         
        
        #PUMP. Now, if it has not been stopped yet and the reward time has passed I am stopping the PUMP by sending 'stp\r\n' 
        if  GameLogic.globalDict['reward'] and (tiempo - GameLogic.globalDict['tiempoLastReward']>GameLogic.globalDict['tiempoReward']):
            GameLogic.globalDict['reward'] = 0
            if GameLogic.globalDict['pump_control'] and GameLogic.globalDict['PUMP'].isOpen():
                word = 'stp\r\n'
                GameLogic.globalDict['PUMP'].write(word) 
                #save commands sent to the pump
                word = 'stopINF\n'
                GameLogic.globalDict['PUMP_commands'].write(word)
                word = "".join(['stp',str(tiempo-GameLogic.globalDict['tiempoLastReward']),'\n'])
                GameLogic.globalDict['PUMP_commands'].write(word) 
                word = '------------------\n'
                GameLogic.globalDict['PUMP_commands'].write(word)
                
                                    
            if GameLogic.globalDict['timeOutExpectation']:
                word = 'exp_trial_end' + tiempo_string
                GameLogic.globalDict['summary'].write(word + '\n')
        
        
        #calculate the effective position (taking into account the angle)
        efective_pos_x = own.position[0] + GameLogic.globalDict['length_effective_position']*own.orientation[0][1] 
        efective_pos_y = own.position[1] + GameLogic.globalDict['length_effective_position']*own.orientation[1][1] 
        
        # finish reinforcement
        if  GameLogic.globalDict['timeOutReinforcement']:
            if (tiempo - GameLogic.globalDict['tiempoLastReinforcement']>GameLogic.globalDict['time_reinforcement']):
                ops.display_blackScreen(scene,own,tiempo)
                GameLogic.globalDict['timeOutReinforcement']  = 0            
          
        # time out. Punishment period ends. 
        #this if statement NEEDS to go before the one concerning the end of the expectation trial
        #since it is here where we turn off the timeOutExpectation flag. Otherwise it would always 
        #enter the if statement corresponding to the expectation trial and would never get the chance 
        #of finishing it.
        elif  GameLogic.globalDict['timeOut']:
            if (tiempo - GameLogic.globalDict['tiempoLastPunishment']>GameLogic.globalDict['endOfTrialDuration']):
                ops.end_of_white_or_black_screen(scene)
                
                if GameLogic.globalDict['airpuff_control']:
                    #airpuff
                    word = 'L\n'
                    GameLogic.globalDict['airPuff'].write(word)
            
                #NEXT TRIAL
                if (random.uniform(0,1)>(GameLogic.globalDict['expectactionProb'])) or (GameLogic.globalDict['timeOutExpectation']==1) or GameLogic.globalDict['passive_trials']: 
                    GameLogic.globalDict['tiempoLastTrial'] = tiempo
                    #position the objects
                    first_time = 0
                    [reward_position,background] = ops.next_reward_position()
                    ops.new_trial(reward_position,own,scene,starting_ori,first_time,GameLogic.globalDict['refferenceRewardLeft'],background)
                    own.orientation = starting_ori.orientation
                    own.position = starting_ori.position  
                    GameLogic.globalDict['timeOutExpectation'] = 0
                else:
                    GameLogic.globalDict['timeOutExpectation'] = 1
                    GameLogic.globalDict['tiempoLastExpectation'] = tiempo
                    expectationFrontWall = scene.objects['expectationFrontWall'] 
                    own.position[0] = expectationFrontWall.position[0]
                    own.position[1] = starting_ori.position[1]
                    word = 'oooooooooooooooooooooooooooooooooo'
                    GameLogic.globalDict['summary'].write(word + '\n')  
                    word = 'exp_trial_start' + tiempo_string
                    GameLogic.globalDict['summary'].write(word + '\n')
       
        # end of expectation period? give reward
        #condition for ending the expectation period
        elif GameLogic.globalDict['timeOutExpectation']:
            if GameLogic.globalDict['spatial_threshold']:
                expectation_trial_end =  ((tiempo - GameLogic.globalDict['tiempoLastExpectation']>GameLogic.globalDict['durationExpectationPeriod']) or efective_pos_y>=GameLogic.globalDict['exp_th']) and not GameLogic.globalDict['reward'] 
            else:
                expectation_trial_end =  (tiempo - GameLogic.globalDict['tiempoLastExpectation']>GameLogic.globalDict['durationExpectationPeriod']) and not GameLogic.globalDict['reward'] 
        
            if  expectation_trial_end:
                if GameLogic.globalDict['pump_control']: 
                    word = 'run\r\n'
                    GameLogic.globalDict['PUMP'].write(word) 
                    #save commands sent to the pump
                    word = 'END_OF_EXPECTATION\n'
                    GameLogic.globalDict['PUMP_commands'].write(word)
                    word = 'startINF\n'
                    GameLogic.globalDict['PUMP_commands'].write(word)
                    word = "".join(['run','\n'])
                    GameLogic.globalDict['PUMP_commands'].write(word) 
                    GameLogic.globalDict['reward'] = 1
                    # update the last reward time
                    GameLogic.globalDict['tiempoLastReward'] = tiempo
                else:
                    word = 'exp_trial_end' + tiempo_string
                    GameLogic.globalDict['summary'].write(word + '\n')  
                
                ops.display_blackScreen(scene,own,tiempo)
               
        elif GameLogic.globalDict['passive_trials']:
            if GameLogic.globalDict['circle_counter']==0 and GameLogic.globalDict['triangle_counter']==0:
                # put the mouse on the reinforcement area        
                own.orientation = starting_ori.orientation
                own.position[1] = GameLogic.globalDict['mousePosPassiveStim']  
                own.position[0] =scene.objects[GameLogic.globalDict['reinforcementWall']].position[0] + 17 
                scene.objects[GameLogic.globalDict['reinforcementWall']].position[2] = -50
                passive_trials.put_the_door(scene,tiempo)
                GameLogic.globalDict['tiempoLastStim'] = tiempo
                word = 'oooooooooooooooooooooooooooooooooo'
                GameLogic.globalDict['summary'].write(word + '\n')  
                word = 'passive_stim_start' + tiempo_string
                GameLogic.globalDict['summary'].write(word + '\n')
                
            elif GameLogic.globalDict['passive_stim'] and (tiempo - GameLogic.globalDict['tiempoLastStim']>GameLogic.globalDict['stimDuration']):
                GameLogic.globalDict['currentPassiveStim'].position[2] = -50
                GameLogic.globalDict['tiempoLastBlackWall'] = tiempo
                GameLogic.globalDict['passive_stim'] = 0
                word = "".join(['blackWall',tiempo_string,'\n'])
                GameLogic.globalDict['passive_stim_seq'].write(word) 
            elif not GameLogic.globalDict['passive_stim'] and (tiempo - GameLogic.globalDict['tiempoLastBlackWall'] + 
                                         GameLogic.globalDict['blackWallDuration']*GameLogic.globalDict['blackWallDurJitter']*(random.random()-1/2) >GameLogic.globalDict['blackWallDuration']):
                passive_trials.next_trial(scene,GameLogic.globalDict['numPassiveTrials'],own,tiempo,starting_ori)                
                GameLogic.globalDict['tiempoLastStim'] = tiempo
                
        else:                         
            # end of trial? 
            #get the reward and fail side walls
            fail_wall = scene.objects[GameLogic.globalDict['punished_object']] 
            reward_wall = scene.objects[GameLogic.globalDict['rewarded_object']] 
            
            #FAIL?
            distance_from_wall = GameLogic.globalDict['current_object'].position[1] - own.position[1]
            vector2_x = 10*(starting_ori.orientation[0][1])
            #Previously we prevented the mouse from turning too much only during the expectation trial
            #If the same happened during a normal trial, the trial ended. Now we also prevent the mouse from turning too much 
            #also during the normal trials. I removed from the 'if' statement this: or (angulo_r>GameLogic.globalDict['turning_angle']).
            #I also removed the code below, which not necessary anymore. Note also that the information saved in the summary file has now
            #a constant 0 in the turning condition, i.e. the trial can never end because the mouse turned too much.
            #vector1_x = 10*(own.orientation[0][1]) #+  own.position[0]
            #vector1_y = 10*(own.orientation[1][1]) #+  own.position[1]
            #vector2_y = 10*(starting_ori.orientation[1][1])     
            #angulo_r =  math.acos(min(1,max(-1,(vector1_x*vector2_x+vector1_y*vector2_y)/(math.sqrt((vector1_x)**2+(vector1_y)**2)*math.sqrt((vector2_x)**2+(vector2_y)**2)))))  
            if  (tiempo - GameLogic.globalDict['tiempoLastTrial']>GameLogic.globalDict['trial_duration']  or \
                 (abs(efective_pos_x-fail_wall.position[0])<=GameLogic.globalDict['x_th'] and efective_pos_y>=GameLogic.globalDict['y_th_fail']) or distance_from_wall<GameLogic.globalDict['marginFail']):
                print(GameLogic.globalDict['y_th_fail'])
                #measure the angle between the starting point and the current position
                vector2_x = (1+math.copysign(1,own.position[0] - starting_ori.position[0]))/2 
                GameLogic.globalDict['performance_history'].append(0)
                own['mean_performance'] = math.floor(100*sum(GameLogic.globalDict['performance_history'])/len(GameLogic.globalDict['performance_history']))
                
                if vector2_x == 0:
                    own['num_left'] = own['num_left'] + 1
                else:
                    own['num_right'] = own['num_right'] + 1
        
          
                GameLogic.globalDict['contadorTrials'] = GameLogic.globalDict['contadorTrials'] + 1
            
                meee = cont.actuators['meee']
                # play the meee
                meee.startSound()
                own['num_fails'] = own['num_fails'] + 1
            
                # write on summary file
                if not GameLogic.globalDict['summary'].closed:
                    word = 'fail'+tiempo_string
                    GameLogic.globalDict['summary'].write(word + '\n')
                    word = 'mean_performance' + str(own['mean_performance'])
                    GameLogic.globalDict['summary'].write(word + '\n')
                    word = 'x' + str(math.floor(own.position[0]*100))  + 'y' + str(math.floor(own.position[1]*100))
                    GameLogic.globalDict['summary'].write(word + '\n')
                    aux = GameLogic.globalDict['tiempoLastTrial']
                    tiempo_string_start = str(aux)
                    tiempo_string_start = tiempo_string_start[0:tiempo_string_start.find('.')+4]
                    word = 'start' +tiempo_string_start  + 'end' +tiempo_string
                    GameLogic.globalDict['summary'].write(word + '\n')
                    word = 'wrongChoice' + str(1*(abs(efective_pos_x-fail_wall.position[0])<=GameLogic.globalDict['x_th'] and efective_pos_y>=GameLogic.globalDict['y_th_fail']))
                    GameLogic.globalDict['summary'].write(word + '\n')
                    word = 'timeout' + str(1*(tiempo - GameLogic.globalDict['tiempoLastTrial']>GameLogic.globalDict['trial_duration']))
                    GameLogic.globalDict['summary'].write(word + '\n')
                    word = 'turning0' #+ str(1*(angulo_r>GameLogic.globalDict['turning_angle']))
                    GameLogic.globalDict['summary'].write(word + '\n')
                
            
            
                own.orientation = starting_ori.orientation
                own.position = starting_ori.position   
            
                              
                #add the walls and change to TRUE the timeout variable
                wall1 = scene.objects['punish_wall1']
                wall2 = scene.objects['punish_wall2']
                wall3 = scene.objects['punish_wall3']
                wall4 = scene.objects['punish_wall4']
                # access actuator and activates it
                wall1.position[0] = own.position[0] + GameLogic.globalDict['walls_margin'] 
                wall1.position[1] = own.position[1] 
                wall1.position[2] = own.position[2] 
                wall2.position[0] = own.position[0] - GameLogic.globalDict['walls_margin'] 
                wall2.position[1] = own.position[1] 
                wall2.position[2] = own.position[2] 
                wall3.position[0] = own.position[0] 
                wall3.position[1] = own.position[1] - GameLogic.globalDict['walls_margin'] 
                wall3.position[2] = own.position[2] 
                wall4.position[0] = own.position[0] 
                wall4.position[1] = own.position[1] + GameLogic.globalDict['walls_margin'] 
                wall4.position[2] = own.position[2] 
                
                GameLogic.globalDict['tiempoLastPunishment'] = tiempo
                GameLogic.globalDict['timeOut'] = 1
                GameLogic.globalDict['endOfTrialDuration'] = GameLogic.globalDict['punishment_duration']
           
           
                if GameLogic.globalDict['airpuff_control']:
                    #airpuff
                    word = 'H\n'
                    GameLogic.globalDict['airPuff'].write(word)
                        
         
            
            #HIT?
            if (abs(efective_pos_x-reward_wall.position[0])<=GameLogic.globalDict['x_th'] and efective_pos_y>=GameLogic.globalDict['y_th_hit']) and (tiempo - GameLogic.globalDict['tiempoLastPunishment']>0.5):
                bell = cont.actuators['bell']
                print(GameLogic.globalDict['y_th_hit'])
                #measure the angle between the starting point and the current position
                vector2_x = (1+math.copysign(1,own.position[0] - starting_ori.position[0]))/2 
                GameLogic.globalDict['performance_history'].append(1)
                own['mean_performance'] = math.floor(100*sum(GameLogic.globalDict['performance_history'])/len(GameLogic.globalDict['performance_history']))
            
            
               
                if vector2_x == 0:
                    own['num_left'] = own['num_left'] + 1
                else:
                    own['num_right'] = own['num_right'] + 1
                   
         
                # ring the bell!
                bell.startSound()
                GameLogic.globalDict['contadorTrials'] = GameLogic.globalDict['contadorTrials'] + 1
            
                own['num_rewards'] = own['num_rewards'] + 1   
                # write on summary file
                if not GameLogic.globalDict['summary'].closed:
                    word = 'hit'+tiempo_string
                    GameLogic.globalDict['summary'].write(word + '\n')
                    word = 'mean_performance' + str(own['mean_performance'])
                    GameLogic.globalDict['summary'].write(word + '\n')
                    word = 'x' + str(math.floor(own.position[0]*100))  + 'y' + str(math.floor(own.position[1]*100))
                    GameLogic.globalDict['summary'].write(word + '\n')
                    aux = GameLogic.globalDict['tiempoLastTrial']
                    tiempo_string_start = str(aux)
                    tiempo_string_start = tiempo_string_start[0:tiempo_string_start.find('.')+4]
                    word = 'start' +tiempo_string_start  + 'end' +tiempo_string
                    GameLogic.globalDict['summary'].write(word + '\n')
        
        
                # put the mouse on the reinforcement area        
                reinforcementWall = scene.objects[GameLogic.globalDict['reinforcementWall']]
                own.orientation = starting_ori.orientation
                own.position[1] = starting_ori.position[1]   
                own.position[0] = reinforcementWall.position[0] + 17 
        
                if GameLogic.globalDict['pump_control']:                
                    # I send the command 'run\r\n' to the PUMP
                    word = 'run\r\n'
                    GameLogic.globalDict['PUMP'].write(word) 
                    #save commands sent to the pump
                    word = 'CORRECT_TRIAL\n'
                    GameLogic.globalDict['PUMP_commands'].write(word)
                    word = 'startINF\n'
                    GameLogic.globalDict['PUMP_commands'].write(word)
                    word = "".join(['RAT ' , str(GameLogic.globalDict['pump_velocity'])])
                    GameLogic.globalDict['PUMP_commands'].write(word) 
                    word = "".join(['dir inf\n'])
                    GameLogic.globalDict['PUMP_commands'].write(word) 
                    word = "".join(['run','\n'])
                    GameLogic.globalDict['PUMP_commands'].write(word) 
                    
                    GameLogic.globalDict['reward'] = 1
                    # update the last reward time
                    GameLogic.globalDict['tiempoLastReward'] = tiempo
            
                                    
                                    
                GameLogic.globalDict['tiempoLastReinforcement'] = tiempo
                GameLogic.globalDict['timeOutReinforcement'] = 1
        
        

        # end of experiment?            
        if tiempo>GameLogic.globalDict['expDuration'] *60+5 or GameLogic.globalDict['contadorTrials']>GameLogic.globalDict['num_trials']:
            if GameLogic.globalDict['still_open']: 
                ops.finish_game(tiempo,own)
                
