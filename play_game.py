from naoqi import ALBroker    
from naoqi import ALProxy

from HanoiGameState import USRHanoiGameState
from TowerOfHanoi.GameState import GameState

import time, sys
import numpy as np
import yaml
import numpy as np

from planner import optimal_action
from planner import get_possible_moves

robot_ip = sys.argv[2]
myBroker = ALBroker("myBroker", "0.0.0.0", 0, robot_ip, 9559)
condition = sys.argv[1]

memory = ALProxy("ALMemory")
move = ALProxy("ALMotion")
tts = ALProxy("ALAnimatedSpeech")
tts.setBodyLanguageModeFromStr("disabled")
posture = ALProxy("ALRobotPosture")
faceTracker = ALProxy("ALFaceDetection")

move.setEnableNotifications(False)

posture._loadPostureLibraryFromName("USRTowerOfHanoi.postures")
posture._generateCartesianMap()
posture.goToPosture("Sit", 1.0)

np.random.seed(42)
number_of_moves = 0

disks = [
    "orange",
    "yellow",
    "green",
    "blue",
    "purple"
]

pole_animations = {
    "start": "tower_of_hanoi/PointStart",
    "middle": "tower_of_hanoi/PointMiddle",
    "finish": "tower_of_hanoi/PointGoal"
}

pole_names = {
    "start": "the pole on your left",
    "middle": "the middle pole",
    "finish": "the pole on your right"    
}

with open("hanoi_config_v2.yaml", 'r') as stream:
    config = yaml.load(stream)

with open("strings.yaml", "r") as stream:
    strings = yaml.load(stream)

def select_line(key):
    weights = list()
    samples = list()
    for x in strings[condition][key]:
        weights.append(x[1])
        samples.append(x[0])
    sum_weights = sum(weights)
    weights = [1.0*x/sum_weights for x in weights]
    
    return np.random.choice(samples, p=weights)


with USRHanoiGameState("USRHanoiGameState2", config) as HanoiGameState:
    try:
        if condition == "social":
            posture.goToPosture("Sit", 1.0)
        else:
            posture.goToPosture("USRLookAtTower", 1.0)

        line = select_line("start")
        tts.say(line.format(num=5))
        tts.say(select_line("explanation"))

        # reset the game
        game_state = HanoiGameState.get_gamestate()
        starting_state = GameState(5, number=341)
        tts.say(select_line("order_disks"))
        while not game_state.is_start():
            game_state = HanoiGameState.get_gamestate()
        tts.say(select_line("begin"))

        # play one round of the game
        is_human_turn = False
        while not game_state.is_goal():
            possible_moves = get_possible_moves(game_state)
            possible_nums = list()
            for move, _ in possible_moves:
                possible_nums.append(move.number)

            disk, from_pole, to_pole = optimal_action(game_state)
            optimal_state = GameState(5, number=game_state.number)
            optimal_state.move(disk, to_pole)

            if not is_human_turn:
                # announce action
                tts.say(select_line("ask_move").format(
                    disk=disk,
                    from_pole=pole_names[from_pole],
                    to_pole=pole_names[to_pole],
                    anim1=pole_animations[from_pole],
                    anim2=pole_animations[to_pole]
                ))

                requested_state = GameState(5, number=game_state.number)
                requested_state.move(disk, to_pole)
            else:
                tts.say(select_line("your_turn"))
                requested_state = None

            # wait until move has been made
            wait_for_move = True
            while wait_for_move:
                next_game_state = HanoiGameState.get_gamestate()
                idx = next_game_state.number
                if next_game_state.number == game_state.number:
                    continue
                elif not is_human_turn and next_game_state.number == requested_state.number:
                    if condition == "social":
                            posture.goToPosture("Sit", 1.0)
                    tts.say(select_line("thank_you"))
                    wait_for_move = False
                    number_of_moves += 1
                elif next_game_state.number in possible_nums:
                    if is_human_turn:
                        tts.say(select_line("move_registered"))
                        if condition == "social":
                            posture.goToPosture("Sit", 1.0)

                        if next_game_state.number == optimal_state.number:
                            if condition == "social":
                                tts.say(select_line("optimal_move"))
                            elif number_of_moves % 5 == 0:
                                tts.say(select_line("optimal_move"))
                        else:
                            tts.say(select_line("suboptimal_move"))

                        wait_for_move = False
                        number_of_moves += 1
                    else:
                        continue
                elif next_game_state.has_missing_disk()[0]:
                    continue
                else:
                    print(next_game_state.has_missing_disk()[0], next_game_state.has_missing_disk())
                    # tts.say("Invalid state")
            game_state = next_game_state
            is_human_turn = not is_human_turn

        tts.say(select_line("congratulations").format(num=5, num_moves=number_of_moves))
    except KeyboardInterrupt:
        myBroker.shutdown()
        sys.exit(0)