#29/08/2012. Adapted code from mouseLook.py. The original code can be found here: http://www.tutorialsforblender3d.com/Game_Engine/MouseLook/blend/MouseLook249.txt

# We control the movement of the mouse, both the back and forward movement and the turning.

import bge,Rasterizer, math, GameLogic, time

def main():
    # get the object
    controller = bge.logic.getCurrentController()
    obj = controller.owner
    
    if obj['endStandbyPeriod']==2:
        # 1. get the size of the screen
        gameScreen = gameWindow(Rasterizer)
        # 2. get the movement of the pointer relative to the screen size
        move = mouseMove(gameScreen,controller,obj)
        tiempo = time.clock() - GameLogic.globalDict['tiempo0']
        tiempo2 = str(tiempo)
        tiempo2 = tiempo2[0:tiempo2.find('.')+4]
        word =  "".join(['go',str(math.floor(move[0]*100)),'turn',str(math.floor(move[1]*100)),'t',tiempo2,"\n"])
        if not GameLogic.globalDict['raw_velocity'].closed:
            GameLogic.globalDict['raw_velocity'].write(word)
        # 3. get the movemment of the pointer and apply it to the object    
        useMouseLook(controller, move,obj)
        # 4. just centre the cursor
        centerCursor(controller, gameScreen, Rasterizer)
    


def gameWindow(Rasterizer):
    # get the size of the screen
    width = Rasterizer.getWindowWidth()
    height = Rasterizer.getWindowHeight()
    return(width, height)


def mouseMove(gameScreen, controller, obj):
    # get the movement of the pointer relative to the screen size
    mouse = controller.sensors['MouseLook']
    width = gameScreen[0]
    height = gameScreen[1]
    
    x = math.floor(width/2) - mouse.position[0]
    y = math.floor(height/2) - mouse.position[1]
    
    if not mouse.positive:
        x = 0 
        y = 0
    
    return(x,y)


def useMouseLook(controller, move, obj):
    # get the movemment of the pointer and apply it to the object provided the radars do not detect an object in the way.
    # radars
    rf = controller.sensors['Radar_front']
    # movemment 
    leftRight = move[1]*GameLogic.globalDict['turnSensitivity']
    goBack = -move[0]*GameLogic.globalDict['backForwardSensitivity']
    goBack = max([goBack,0])
    if  not GameLogic.globalDict['timeOut'] and not GameLogic.globalDict['timeOutReinforcement'] and not GameLogic.globalDict['passive_trials']:
        #I will now make a running average of the turn to remove noise. First I add the new turning value to the turnning history
        if len(GameLogic.globalDict['turn_history'])<GameLogic.globalDict['average_window']:
            GameLogic.globalDict['turn_history'].append(leftRight)
            GameLogic.globalDict['backForward_history'].append(goBack)
        else:
            GameLogic.globalDict['turn_history'][0:GameLogic.globalDict['average_window']-1] = GameLogic.globalDict['turn_history'][1:GameLogic.globalDict['average_window']] 
            aux = leftRight
            GameLogic.globalDict['turn_history'][GameLogic.globalDict['average_window']-1] = aux
            GameLogic.globalDict['backForward_history'][0:GameLogic.globalDict['average_window']-1] = GameLogic.globalDict['backForward_history'][1:GameLogic.globalDict['average_window']] 
            aux = goBack
            GameLogic.globalDict['backForward_history'][GameLogic.globalDict['average_window']-1] = aux
    else:
        GameLogic.globalDict['turn_history'] = [0]*len(GameLogic.globalDict['turn_history'])
        GameLogic.globalDict['backForward_history'] = [0]*len(GameLogic.globalDict['backForward_history'])
        
    # and then I average all the values of the turn history             
    leftRight = sum(GameLogic.globalDict['turn_history'])/len(GameLogic.globalDict['turn_history'])
    goBack = sum(GameLogic.globalDict['backForward_history'])/len(GameLogic.globalDict['backForward_history'])
   # actuators
    act_LeftRight = controller.actuators["LeftRight"]
    act_GoBack = controller.actuators["GoBack"]
 
    # control that radars do not detect anything in the way. id they do, I make sure that the mouse can not move towards the object
    if rf.positive:
        goBack = 0

    #Previously we prevented the mouse from turning too much only during the expectation trial
    #If the same happened during a normal trial, the trial ended. Now we applied the former 
    #procedure to all types of trials.
    #if GameLogic.globalDict['timeOutExpectation']==1:
    scene = bge.logic.getCurrentScene()
    starting_ori = scene.objects['starting_orientation']
    vector1_x = 10*(obj.orientation[0][1]) #+  obj.position[0]
    vector1_y = 10*(obj.orientation[1][1]) #+  obj.position[1]
    vector2_x = 10*(starting_ori.orientation[0][1])
    vector2_y = 10*(starting_ori.orientation[1][1])     
    angulo_r =  math.copysign(1,vector2_x-vector1_x)*math.acos(min(1,max(-1,(vector1_x*vector2_x+vector1_y*vector2_y)/(math.sqrt((vector1_x)**2+(vector1_y)**2)*math.sqrt((vector2_x)**2+(vector2_y)**2)))))  
    #else:
    #    angulo_r = 0    
    #angulo_r = 0 
    if angulo_r<-GameLogic.globalDict['turning_angle']:
        leftRight = max(leftRight,0)
    elif angulo_r>GameLogic.globalDict['turning_angle']:
        leftRight = min(leftRight,0)
        
        
    #apply rotation to the global orientation
    act_LeftRight.dRot = [ 0.0, 0.0, leftRight]
    act_LeftRight.useLocalDRot = False
    # apply back and forward movement to the local position
    act_GoBack.dLoc = [0, goBack , 0]
    act_GoBack.useLocalDLoc = True

    # activate actuators
    controller.activate(act_LeftRight)
    controller.activate(act_GoBack)
    

def centerCursor(controller, gameScreen, Rasterizer):
    # just centre the cursor
    width = gameScreen[0]
    height = gameScreen[1]
    mouse = controller.sensors["MouseLook"]
    pos = mouse.position
    if pos != [ width/2, height/2]:
        Rasterizer.setMousePosition(math.floor(width/2), math.floor(height/2))
    else:
        # I deactivate the actuators. I am not sure why I have to do this....
        act_LeftRight = controller.actuators["LeftRight"]
        controller.deactivate(act_LeftRight)
        act_GoBack = controller.actuators["GoBack"]
        controller.deactivate(act_GoBack)
        
   