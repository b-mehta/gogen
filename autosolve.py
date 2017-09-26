#!/usr/bin/env python
from collections import deque
import argparse
import textwrap
import gogen


class SolveGogen(gogen.Gogen):
    def __init__(self, filename, verbose=False):
        gogen.Gogen.__init__(self)
        self.readfile(filename)
        self.verbose = verbose

        # Create the constraint store.
        self.c_store = self.pairs.copy()

        # Create the knowledge base.
        places = {(i, j) for i in range(5) for j in range(5)}
        self.knowledge = {letter: places.copy() for letter in gogen.alpha}

        self.queue = deque()
        self.updated = set()

        # Predefine what the neighbourhood of each point is.
        self.neighbours = {(i, j): self._moore(i, j) for (i, j) in places}

        # Set up board from already known information.
        for letter in gogen.alpha:
            place = self.fixed.get(letter)
            if place:
                self.knowledge[letter] = {place}
                self.check_solved_letter(letter)

    def _moore(self, x, y):
        def region(t):
            return range(max(0, t-1), min(t+1, 4) + 1)

        result = {(i, j) for i in region(x) for j in region(y)}

        return result - {(x, y)}

    def _group_neighbours(self, positions):
        answer = set()
        for (x, y) in positions:
            answer.update(self.neighbours[x, y])
        return answer

    def spread_constraint_from_letter(self, letter):
        if self.verbose >= 2:
            print('Propagating on', letter)

        allowed = self._group_neighbours(self.knowledge[letter])

        if letter in self.fixed:
            neighbours = self.c_store.pop(letter)
        else:
            neighbours = self.c_store.get(letter)

        if self.verbose >= 2:
            print('Neighbours', neighbours)

        for other in neighbours:
            if other in self.fixed:
                print('{0} was on {1}\'s list...'.format(other, letter))

            revised = allowed.intersection(self.knowledge[other])

            if self.knowledge[other] != revised:
                self.knowledge[other] = revised
                self.updated.add(other)

    def remove_constraints(self, letter, place):
        for other in gogen.alpha:
            if other in self.c_store and letter in self.c_store[other]:
                self.c_store[other].remove(letter)

            if other in self.fixed:
                continue

            if place in self.knowledge[other]:
                self.knowledge[other].discard(place)
                self.updated.add(other)

    def check_solved_letter(self, letter):
        new = self.knowledge[letter]

        if len(new) <= 1:
            if len(new) == 0:
                print('unsolvable!')
                return

            place = list(new)[0]
            if self.verbose >= 2:
                print('Bound {0} at {1}'.format(letter, place))
            self.fixed[letter] = {place}
            self.board[place[0]][place[1]] = letter

            if letter in self.queue:
                self.queue.remove(letter)
            self.queue.appendleft(letter)

            self.remove_constraints(letter, place)

        if letter not in self.queue:
            self.queue.append(letter)

    def solve(self):
        count = 0
        while self.queue and count < 100 and len(self.fixed) < 25:
            current = self.queue.popleft()
            if not self.c_store.get(current):
                continue

            if self.verbose >= 2:
                print(self.c_store)
                print(self.queue)

            self.spread_constraint_from_letter(current)

            while self.updated:
                if self.verbose >= 2:
                    print(self.updated)

                check = self.updated.copy()
                self.updated = set()
                for letter in check:
                    self.check_solved_letter(letter)

            if self.verbose >= 3:
                for i in gogen.alpha:
                    print(i, self.knowledge[i])

            count += 1

            if self.verbose >= 1:
                print(count, board, sep='\n', end='\n\n')

        if not self.queue:
            print('queue empty')
        elif count >= 100:
            print('passed 100 steps')
        elif len(self.fixed) == 25:
            print('solved!')
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('puzzles', nargs='*', type=str,
                        default=['Puzzles/43.txt'],
                        help='a list of puzzles to solve')
    parser.add_argument('-v', '--verbose', help='increase output verbosity',
                        action='count', default=0)

    args = parser.parse_args()

    for location in args.puzzles:
        print(location)
        board = SolveGogen(location, verbose=args.verbose)
        board.solve()
