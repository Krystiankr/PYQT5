import pandas as pd


class DataOperations:
    def __init__(self):
        self.df = pd.read_csv('control/Data.csv', encoding='utf8')

    def sample_row(self):
        random = self.df[self.df.Frequency == self.df.Frequency.min()]
        return random.sample()

    def get_polish_word(self, row):
        return row['Polski'].values[0]

    def get_english_word(self, row):
        return row['Angielski'].values[0]

    def get_sample_polish(self):
        return self.get_polish_word(self.sample_row())
