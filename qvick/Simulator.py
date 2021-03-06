import os
import sys
import numpy as np


class Simulator:
    def __init__(self, main, f1, f2):
        self.pos = (0, 19)
        self.dir = 1  # 0=North, 1=East, 2=South, 3=West
        self.steps = 0
        self.debug = False
        self.f1 = f1
        self.f2 = f2
        self.main = main
        self._map = np.load(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'qvik_array.npy'))[:, :, 0]

    def _print_position(self):
        if self.debug:
            print('{s}: ({p1}, {p2})'.format(s=self.steps, p1=self.pos[0], p2=self.pos[1]))

    def _move(self, l):
        """Move

        :param l: Step length: 1 for forward, -1 for backward
        """

        if self.dir == 0:
            next_pos = (self.pos[0], self.pos[1] - l)  # Up
        elif self.dir == 1:
            next_pos = (self.pos[0] + l, self.pos[1])  # Right
        elif self.dir == 2:
            next_pos = (self.pos[0], self.pos[1] + l)  # Down
        else:
            next_pos = (self.pos[0] - l, self.pos[1])  # Left

        # Next step is inside the map and is not a wall -> move to next step
        if 0 <= self.pos[0] < 20 and 0 <= self.pos[1] < 20 and self._map[next_pos[1]][next_pos[0]]:
            self.pos = next_pos
        self.steps += 1
        self._print_position()

        if self.pos == (19, 0):
            # Goal reached
            print('Success with configuration')
            print(self.steps)
            print(self.main)
            print(self.f1)
            print(self.f2)
            sys.exit()

    def forward(self):
        self._move(1)

    def backward(self):
        self._move(-1)

    def right(self):
        self.dir += 1
        if self.dir == 4:
            self.dir = 0

    def left(self):
        self.dir -= 1
        if self.dir == -1:
            self.dir = 3

    def _run_command(self, command_name):
        if self.steps > 1000:
            print('Max steps exceeded')
            raise ValueError(-1)

        if command_name == 'forward':
            self.forward()
        elif command_name == 'backward':
            self.backward()
        elif command_name == 'right':
            self.right()
        elif command_name == 'left':
            self.left()
        elif command_name == 'f1':
            for com in self.f1:
                self._run_command(com)
        elif command_name == 'f2':
            for com in self.f2:
                self._run_command(com)

    def run(self):
        self._print_position()
        for com in self.main:
            self._run_command(com)
        print('Did not reach goal')
        raise ValueError(0)

if __name__ == '__main__':
    # Generate data
    import random
    from itertools import permutations
    a = ['forward', 'backward', 'left', 'right', 'f1', 'f2']
    perm = list(permutations(a, len(a)))
    # permm = list(permutations(range(3), 3))
    possibilities = []
    for p in perm:
        for i in range(10):
            possibilities.append({
                'main': ['f1'],
                'f1': [p[i] for i in sorted(random.sample(range(len(p)), 3))],
                'f2': [p[i] for i in sorted(random.sample(range(len(p)), 3))]})

    for possiblity in possibilities:
        s = Simulator(
            main=possiblity['main'],
            f1=possiblity['f1'],
            f2=possiblity['f2'])
        # s.debug = True

        try:
            s.run()
        except Exception:
            pass
