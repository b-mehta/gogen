"""Store and solve gogen puzzles."""
import string

alpha = string.ascii_uppercase[:-1]


class Gogen(object):
    """Represent a gogen puzzle."""

    def __init__(self):
        """Create an empty board."""
        self.fixed = {}
        self.board = [[None] * 5 for i in range(5)]
        self.pairs = {key: [] for key in alpha}

    def readfile(self, filename):
        """Fill the board with data from file."""
        with open(filename) as input_data:
            lines = input_data.read()

        lines = lines.splitlines()

        # Fill the existing board state.
        for (i, line) in enumerate(lines[:3]):
            for (j, letter) in enumerate(line):
                self.board[i * 2][j * 2] = letter
                self.fixed[letter] = (i * 2, j * 2)

        # Store the words as pairs of letters that must be connected.
        for word in lines[4:]:
            for i in range(len(word) - 1):
                self.pairs[word[i + 1]].append(word[i])
                self.pairs[word[i]].append(word[i + 1])

        # Sort and remove duplicates from the connection list.
        for key in self.pairs:
            self.pairs[key] = sorted(set(self.pairs[key]))

    def __str__(self):
        """Display the board as it is currently."""
        result = []
        for row in self.board:
            line = ' '.join(i if i is not None else '_' for i in row)
            result.append(line)
        return '\n'.join(result)


if __name__ == '__main__':
    test = Gogen()
    test.readfile('Puzzles/07.txt')
    print(test)
    print(test.pairs)
    print(test.fixed)
