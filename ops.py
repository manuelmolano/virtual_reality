import  GameLogic, math, random, bge, time

def get_data_from_VRparams(reference):
    aux = GameLogic.globalDict['params'].find(reference)
    data_aux = GameLogic.globalDict['params'][aux+len(reference)+1:]
    data = data_aux[0:data_aux.find('#')]
    return(data)

def new_trial(reward_position,own,scene,starting_ori,first_time,reward_position_reference,background):
        #remove the walls from previous trial
        if not first_time:
            wall_ori = scene.objects['wallsOrientation']
            GameLogic.globalDict['current_object'].position[2] = -50
            GameLogic.globalDict['current_object'].orientation = wall_ori.orientation
            fail_wall = scene.objects[GameLogic.globalDict['punished_object']] 
            reward_wall = scene.objects[GameLogic.globalDict['rewarded_object']] 
            fail_wall.position[2] = -50
            reward_wall.position[2] = -50
            GameLogic.globalDict['backgroundObject'].position[2] = -50
        
        
        #current reward and fail objects
        GameLogic.globalDict['punished_object'] = GameLogic.globalDict['punished_objectList'][background]
        GameLogic.globalDict['rewarded_object'] = GameLogic.globalDict['rewarded_objectList'][background]
    
        #position the objects
        random.shuffle(GameLogic.globalDict['objects_list'])
        objeto = scene.objects[GameLogic.globalDict['objects_list'][0]]   
        GameLogic.globalDict['current_object'] = objeto
        #object (wall) position
        objeto.position[0] = GameLogic.globalDict['distance_mouse_obj']*starting_ori.orientation[0][1] + starting_ori.position[0]
        objeto.position[1] = GameLogic.globalDict['distance_mouse_obj']*starting_ori.orientation[1][1] + starting_ori.position[1]  
        objeto.position[2] = starting_ori.position[2] + GameLogic.globalDict['wall_Z_component']  
        objeto.applyRotation([0,0,reward_position],0)
           
               
        #this is for the black wall behind the rewarded door 
        GameLogic.globalDict['backgroundObject'] = scene.objects[GameLogic.globalDict['background_walls'][background]] 
        GameLogic.globalDict['backgroundObject'].position[1] = objeto.position[1] + GameLogic.globalDict['background_object_margin']
        GameLogic.globalDict['backgroundObject'].position[2] = starting_ori.position[2]+ GameLogic.globalDict['background_object_Z']
        GameLogic.globalDict['backgroundObject'].position[0] = objeto.position[0] 
         
        #we need to check on which side is the rewarded door to put the invisible object there
        wallTriangles = scene.objects[GameLogic.globalDict['triangleWalls'][background]]  
        wallTriangles.position[1] = 55
        wallTriangles.position[2] = 8
        wallCircles = scene.objects[GameLogic.globalDict['circleWalls'][background]]  
        wallCircles.position[1] = 55
        wallCircles.position[2] = 8
        if reward_position==0:
            wallCircles.position[0] = starting_ori.position[0] + GameLogic.globalDict['sideDisplacementWalls']
            wallTriangles.position[0] = starting_ori.position[0] - GameLogic.globalDict['sideDisplacementWalls']
        else:
            wallCircles.position[0] = starting_ori.position[0] - GameLogic.globalDict['sideDisplacementWalls']
            wallTriangles.position[0] = starting_ori.position[0] + GameLogic.globalDict['sideDisplacementWalls']
            
            
        if first_time==1:            
            word = 'version3.0'
            GameLogic.globalDict['summary'].write(word + '\n') 
            for key in GameLogic.globalDict.keys():
                if key!='params':
                    word = key + '=' + str(GameLogic.globalDict[key]) 
                    GameLogic.globalDict['summary'].write(word + '\n') 
            back_wall = scene.objects['wallLeft.001']  
            word = 'front_wall' + str(math.floor(objeto.position[1]*100))  + '/' + str(math.floor(objeto.position[0]*100))
            GameLogic.globalDict['summary'].write(word + '\n') 
            word = 'back_wall' + str(math.floor(back_wall.position[1]*100))  + '/' + str(math.floor(back_wall.position[0]*100))
            GameLogic.globalDict['summary'].write(word + '\n') 
            word = 'wall1_' + str(math.floor(wallCircles.position[1]*100))  + '/' + str(math.floor(wallCircles.position[0]*100))
            GameLogic.globalDict['summary'].write(word + '\n')
            word = 'wall2_' + str(math.floor(wallTriangles.position[1]*100))  + '/' + str(math.floor(wallTriangles.position[0]*100))
            GameLogic.globalDict['summary'].write(word + '\n')
            word = 'theshold_x' + str(math.floor(GameLogic.globalDict['x_th']*100))  
            GameLogic.globalDict['summary'].write(word + '\n')
            word = 'theshold_y_hit' + str(math.floor(GameLogic.globalDict['y_th_hit']*100))  
            GameLogic.globalDict['summary'].write(word + '\n')
            word = 'theshold_y_fail' + str(math.floor(GameLogic.globalDict['y_th_fail']*100))  
            GameLogic.globalDict['summary'].write(word + '\n')
            word = 'length_effective_position_' + str(GameLogic.globalDict['length_effective_position'])
            GameLogic.globalDict['summary'].write(word + '\n')
            
            
        if not GameLogic.globalDict['summary'].closed:
            word = 'oooooooooooooooooooooooooooooooooo'
            GameLogic.globalDict['summary'].write(word + '\n')
            word = 'obj' + GameLogic.globalDict['objects_list'][0]
            GameLogic.globalDict['summary'].write(word + '\n')
            word = 'flip' + str(1*(reward_position==reward_position_reference))
            GameLogic.globalDict['summary'].write(word + '\n')
            word = 'bg'+GameLogic.globalDict['background_walls'][background]
            GameLogic.globalDict['summary'].write(word + '\n')
            word = 'manualControl' + str(GameLogic.globalDict['manualControlPresentation']) 
            GameLogic.globalDict['summary'].write(word + '\n')
       
            
            
def next_reward_position():
    #we first choose the position of the reward
    #manual control
    if GameLogic.globalDict['manualControlPresentation']:
        reward_position = GameLogic.globalDict['flip_list'][GameLogic.globalDict['LeftRight']]
    elif len(GameLogic.globalDict['sides_mat'])>=GameLogic.globalDict['numb_data_pseudoRandom']:       
        if sum(GameLogic.globalDict['sides_mat'])/len(GameLogic.globalDict['sides_mat']) ==1:
            reward_position = GameLogic.globalDict['flip_list'][1]
        elif sum(GameLogic.globalDict['sides_mat'])/len(GameLogic.globalDict['sides_mat']) ==0:
            reward_position = GameLogic.globalDict['flip_list'][0]  
        else:
            aux = [0,1]
            random.shuffle(aux)
            reward_position = GameLogic.globalDict['flip_list'][aux[0]]  
    else:
        aux = [0,1]
        random.shuffle(aux)
        reward_position = GameLogic.globalDict['flip_list'][aux[0]]  
        
            
    if len(GameLogic.globalDict['sides_mat'])<GameLogic.globalDict['numb_data_pseudoRandom']:
        GameLogic.globalDict['sides_mat'].append(1*(reward_position==0))
    else:
        GameLogic.globalDict['sides_mat'][0:GameLogic.globalDict['numb_data_pseudoRandom']-1] = GameLogic.globalDict['sides_mat'][1:GameLogic.globalDict['numb_data_pseudoRandom']] 
        aux = 1*(reward_position==0)
        GameLogic.globalDict['sides_mat'][GameLogic.globalDict['numb_data_pseudoRandom']-1] = aux    
            
    #now select the background
    background = random.randint(0, len(GameLogic.globalDict['background_walls'])-1)
        
        
              
    return(reward_position,background)        


def finish_game_keyboard():
    #This code just close the ports we have opened to comunicate with the PUMP and simulink and finish the game by activating and actuator called 'Game' that has already been set up.
    cont = bge.logic.getCurrentController()
    own = cont.owner
    keyboard = cont.sensors['finish (space)']
    if keyboard.status==1:
        tiempo = time.clock() - GameLogic.globalDict['tiempo0']
        finish_game(tiempo,own)

def finish_game(tiempo,own):
    print('Number of rewards: ')
    print(own['num_rewards'])
    print('Number of fails: ')
    print(own['num_fails'])
    print('Duration: ')
    print(str(math.floor(tiempo*100)/100)+'s')
    print('#####################################################')
        
    word = 'num_rewards' +' '+ str(own['num_rewards'])
    GameLogic.globalDict['log'].write(word + '\n')
    word = 'num_fails' +' '+ str(own['num_fails'])
    GameLogic.globalDict['log'].write(word + '\n')
    word = 'duration' +' '+ str(math.floor(tiempo*100)/100)
    GameLogic.globalDict['log'].write(word + '\n')
    word = 'mean_performance' +' '+ str(own['mean_performance'])
    GameLogic.globalDict['log'].write(word + '\n')
    word = 'num_right' +' '+ str(own['num_right'])
    GameLogic.globalDict['log'].write(word + '\n')
    word = 'num_left' +' '+ str(own['num_left'])
    GameLogic.globalDict['log'].write(word + '\n')
               
    word = '-------------------------'
    GameLogic.globalDict['summary'].write(word + '\n')
    word = 'num_rewards' + str(own['num_rewards'])
    GameLogic.globalDict['summary'].write(word + '\n')
    word = 'num_fails' + str(own['num_fails'])
    GameLogic.globalDict['summary'].write(word + '\n')
    word = 'duration' + str(math.floor(tiempo*100)/100)
    GameLogic.globalDict['summary'].write(word + '\n')
    word = 'mean_performance' + str(own['mean_performance'])
    GameLogic.globalDict['summary'].write(word + '\n')
    word = 'num_right' + str(own['num_right'])
    GameLogic.globalDict['summary'].write(word + '\n')
    word = 'num_left' + str(own['num_left'])
    GameLogic.globalDict['summary'].write(word + '\n')
    if GameLogic.globalDict['send']:
        # closes serial por for simulink
        GameLogic.globalDict['ser'].close()
    if GameLogic.globalDict['airpuff_control']:        
        word = 'L'
        if GameLogic.globalDict['airPuff'].isOpen():
            GameLogic.globalDict['airPuff'].write(word) 
            GameLogic.globalDict['airPuff'].close()
        
    if GameLogic.globalDict['pump_control']:       
        # before closing the serial port for the PUMP makes sure it is not pumping...
        word = 'stp\r\n'
        if GameLogic.globalDict['PUMP'].isOpen():
            GameLogic.globalDict['PUMP'].write(word) 
            # closes the serial port    
            GameLogic.globalDict['PUMP'].close()
            GameLogic.globalDict['PUMP_commands'].close()
            
    GameLogic.globalDict['file'].close()
    GameLogic.globalDict['summary'].close()   
    GameLogic.globalDict['log'].close()        
    GameLogic.globalDict['raw_velocity'].close()
    GameLogic.globalDict['passive_stim_seq'].close()
    # access actuator and activates it
    cont = bge.logic.getCurrentController()
    act = cont.actuators["Game"]
    cont.activate(act)
    GameLogic.globalDict['still_open']  = 0
 
    
def display_blackScreen(scene,own,tiempo):
    #add the walls and change to TRUE the timeout variable
    if own['endStandbyPeriod']==2:
        GameLogic.globalDict['tiempoLastPunishment'] = tiempo #after the reinforcement the black walls are shown. They will be removed in line 269
        GameLogic.globalDict['endOfTrialDuration'] = GameLogic.globalDict['afterReward_blackWall_duration']
    wall1 = scene.objects['reward_wall4']
    wall2 = scene.objects['reward_wall3']
    wall3 = scene.objects['reward_wall2']
    wall4 = scene.objects['reward_wall1']
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
    GameLogic.globalDict['timeOut'] = 1
       
    
def end_of_white_or_black_screen(scene):    
    GameLogic.globalDict['timeOut'] = 0
    wall1 = scene.objects['punish_wall1']
    wall2 = scene.objects['punish_wall2']
    wall3 = scene.objects['punish_wall3']
    wall4 = scene.objects['punish_wall4']
    # access actuator and activates it
    wall1.position[2] = -10
    wall2.position[2] = -10
    wall3.position[2] = -10 
    wall4.position[2] = -10
    wall1 = scene.objects['reward_wall1']
    wall2 = scene.objects['reward_wall2']
    wall3 = scene.objects['reward_wall3']
    wall4 = scene.objects['reward_wall4']
    # access actuator and activates it
    wall1.position[2] = -10
    wall2.position[2] = -10
    wall3.position[2] = -10 
    wall4.position[2] = -10