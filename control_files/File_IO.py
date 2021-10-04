class File:
    def __init__(self, r_w="r", file="control_files/Scores.txt"):
        self.file = open(file, r_w)

    def print(self, line):
        print(self.file.readlines()[line][12:], end='')

    def return_strike(self):
        return int(self.file.readlines()[2][12:])

    def return_lines(self):
        return self.file.readlines()

    def write_lines(self, lines):
        self.file.writelines(lines)

    def return_correct(self):
        print(2)
        return self.file.readlines()

    def close(self):
        self.file.close()

    def write_end(self, text=""):
        self.file.write(text+"\n")