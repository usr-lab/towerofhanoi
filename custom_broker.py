from naoqi import ALBroker    
from naoqi import ALProxy

from HanoiGameState import USRHanoiGameState

import time, sys

import numpy as np
import cv2

robot_ip = "love"
myBroker = ALBroker("myBroker", "0.0.0.0", 0, robot_ip, 9559)

memory = ALProxy("ALMemory")
move = ALProxy("ALMotion")
speak = ALProxy("ALTextToSpeech")
posture = ALProxy("ALRobotPosture")

posture._loadPostureLibraryFromName("USRTowerOfHanoi.postures")
posture._generateCartesianMap()

rolling_fps = np.zeros((100,1))
rolling_idx = 0

with USRHanoiGameState("USRHanoiGameState2") as HanoiGameState:
    # HanoiGameState.configure()
    try:
        while True:
            # foo =  raw_input("Robot says: ")
            # speak.say(foo)
            time_start = time.time()
            state = HanoiGameState.updateGameState()
            frame_time = time.time()-time_start
            rolling_fps[rolling_idx] = frame_time
            rolling_idx = int((rolling_idx + 1) % 100)
            
            actual_fps = sum(rolling_fps != 0) / sum(rolling_fps)
            print("Actual FPS {sec}".format(sec=actual_fps))
            
            # time.sleep(100)
    except KeyboardInterrupt:
        myBroker.shutdown()
        sys.exit(0)