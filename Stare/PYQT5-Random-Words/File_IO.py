class File:
    def __init__(self, r_w="r"):
        if r_w == "w":
            self.file = open("Scores.txt", "w")

        if r_w == "r":
            self.file = open("Scores.txt", "r")

    def print(self, line):
        print(self.file.readlines()[line][12:], end='')

    def return_strike(self):
        return int(self.file.readlines()[2][12:])

    def return_lines(self):
        return self.file.readlines()
# 222 222
    def write_lines(self, lines):
        self.file.writelines(lines)

    def return_correct(self):
        print(2)
        return self.file.readlines()

    def close(self):
        self.file.close()
