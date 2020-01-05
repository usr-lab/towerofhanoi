import numpy as np

from planner import is_goal
from planner import optimal_action
from planner import state_to_num, num_to_state
from planner import get_possible_moves

disks = [
    "orange",
    "yellow",
    "green",
    "blue",
    "purple"
]

poles = [
    "left",
    "middle",
    "right"
]


def play_game(num_disks):
    # reset the game
    game_state = np.array((2, 2, 2, 2, 2))
    starting_state = np.array((0, 0, 0, 0, 0))
    while state_to_num(game_state) != state_to_num(starting_state):
        state = raw_input("Waiting for the starting state to be achieved. Please type it (seperated by spaces): ")
        game_state = np.array([int(el) for el in state.split(" ")])

    # play one round of the game
    is_human_turn = True
    while not is_goal(game_state):
        possible_moves = get_possible_moves(game_state)
        possible_nums = list()
        for move, _ in possible_moves:
            possible_nums.append(state_to_num(move))

        print ("The current game state is: " + str(game_state))
        if not is_human_turn:
            print("My Turn")
            disk, from_pole, to_pole = optimal_action(game_state)

            # announce action
            print("Please move the {disk} from the {from_pole} pole to the {to_pole} one.".format(
                disk=disks[disk],
                from_pole=poles[from_pole],
                to_pole=poles[to_pole]
            ))

            requested_state = game_state.copy()
            requested_state[disk] = to_pole
            requested_state_num = state_to_num(requested_state)
        else:
            print("Your Turn. Possible moves are: ")
            print([move for move, _ in possible_moves])
            requested_state = None

        # wait until move has been made
        wait_for_move = True
        while wait_for_move:
            state = raw_input("Please input the next state (seperated by spaces): ")
            next_game_state = np.array([int(el) for el in state.split(" ")])
            idx = state_to_num(next_game_state)
            if state_to_num(next_game_state) == state_to_num(game_state):
                print("Same State Detected, doing nothing!")
                continue
            elif not is_human_turn and state_to_num(next_game_state) == requested_state_num:
                print("Thank you!")
                wait_for_move = False
            elif state_to_num(next_game_state) in possible_nums:
                if is_human_turn:
                    print("Valid move deteted!")
                    wait_for_move = False
                else:
                    print("I'm sorry, this is not the move I've asked for.")
                    continue
            else:
                print("Invalid move, please correct the game state.")
                continue
        game_state = next_game_state
        is_human_turn = not is_human_turn

    print("Very nice! We have won the game with {0} disks!".format(num_disks))


if __name__ == "__main__":
    play_game(5)