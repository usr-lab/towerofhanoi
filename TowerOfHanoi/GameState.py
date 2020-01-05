import numpy as np

from Disk import Disk

class GameState(object):
    pole_names = ["None", "start", "middle", "finish"]
    num_disk_positions = len(pole_names)

    def __init__(self, num_disks, number=None):
        self.disks = list()
        self.disks_by_name = dict()
        self.disk_names = list()

        disk_names = ["orange", "yellow", "green", "blue", "purple"]

        for idx in range(num_disks):
            disk = Disk()
            disk_name = disk_names[idx]

            self.disks.append(disk)
            self.disks_by_name[disk_names[idx]] = disk
            self.disk_names.append(disk_name)

        if number is not None:
            pos = self.num_disk_positions
            rest = number
            for disk_name in reversed(disk_names):
                disk = self.disks_by_name[disk_name]
                disk_idx = disk_names.index(disk_name)
                pole_idx = rest // pos ** disk_idx

                disk.pole = pole_idx
                rest = rest - pole_idx * pos ** disk_idx

    @property
    def array(self):
        return np.array([disk.pole for disk in self.disks])

    def __str__(self):
        lines = ["{disk} is on pole {pole}".format(disk=self.disk_names[idx], 
                                                   pole=self.pole_names[pole])
                    for idx, pole in enumerate(self.array)]
        
        return "\n".join(lines)

    def __repr__(self):
        return "Tower of Hanoi GameState ID {id}".format(id=self.number)

    @property
    def number(self):
        pos = self.num_disk_positions

        number = 0
        for disk_idx, disk in enumerate(self.disks):
            pole_idx = disk.pole
            increment = pole_idx * pos ** disk_idx
            number += increment

        return number

    def move(self, disk_name, pole_name):
        disk = self.disks_by_name[disk_name]
        pole = self.pole_names.index(pole_name)

        disk.pole = pole

    def has_missing_disk(self):
        for disk_name, disk in self.disks_by_name.items():
            if disk.pole == 0:
                return (True, disk_name)
        else:
            return (False, None)

    def is_goal(self):
        for disk in self.disks:
            if self.pole_names[disk.pole] != "finish":
                return False
        
        return True

    def is_start(self):
        for disk in self.disks:
            if self.pole_names[disk.pole] != "start":
                return False

        return True

if __name__ == "__main__":
    foo = GameState(5)
    foo.move("orange", "start")
    foo.move("yellow", "finish")
    foo.move("green", "start")
    foo.move("blue", "middle")
    foo.move("purple", "finish")

    goal_state = GameState(5)
    goal_state.move("orange","finish")
    goal_state.move("yellow","finish")
    goal_state.move("green","finish")
    goal_state.move("blue","finish")
    goal_state.move("purple","finish")

    starting_state = GameState(5)
    starting_state.move("orange","start")
    starting_state.move("yellow","start")
    starting_state.move("green","start")
    starting_state.move("blue","start")
    starting_state.move("purple","start")

    bar = GameState(4)
    bar.move("orange","finish")
    bar.move("yellow","finish")
    bar.move("green","finish")
    bar.move("blue","finish")

    print(bar, bar.number)