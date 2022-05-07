import pandas as pd


class Data:
    def __init__(self):
        self.df = pd.read_csv('control_files/Data.csv', encoding = 'utf8')

    def print_df(self):
        print(self.df)

    def len_df(self):
        return len(self.df)

    def df_return(self):
        return self.df

    def set_at(self, at_0, at_1, what):
        self.df.at[at_0, at_1] = what

    def col_0(self):
        return 'Angielski'

    def col_1(self):
        return 'Polski'

    def df_random_return(self):
        return self.df[self.df['Frequency'] == self.df['Frequency'].min()]

    def len_random(self):
        return len(self.df[self.df['Frequency'] == self.df['Frequency'].min()])

    def reset_df(self):
        self.df = pd.read_csv('control_files/Data.csv')

    def sample_row(self):
        random = self.df[self.df.Frequency == self.df.Frequency.min()]
        return random.sample()
        #return self.df[self.df['Frequency'] == self.df['Frequency'].min()].sample()

    def increase_perfectScore(self, word, reset=False):
        if reset:
            self.df.at[self.df[self.df['Angielski'] == word].index[0], 'PerfectScore'] = 0
        else:
            self.df.at[self.df[self.df['Angielski'] == word].index[0], 'PerfectScore'] += 1
        return self.df.at[self.df[self.df['Angielski'] == word].index[0], 'PerfectScore']

    def increase_frequency(self, word, number=1):
        self.df.at[self.df[self.df['Angielski'] == word].index[0], 'Frequency'] += number

    def increaseBadlyAnswer(self, word):
        self.df.at[self.df[self.df['Angielski'] == word].index[0], 'BadlyAnswer'] += 1

    def add_new_word(self, ang, pol):
        try:
            if ang == "" or pol == "":
                return "Word can't be empty!!"
            if not self.is_there_word(ang): # after = columns Col1, Col2, Frequency, Badly, PerfectScore
                self.df.loc[self.df.index.max() + 1] = [ang] + [pol] + [self.df['Frequency'].min()] + [0] + [0]
                return f"Added new word [{ang}]"
            else:
                return f"The word already exists [{ang}]"
        except Exception:
            return f"ERROR, while adding new word"

    def is_there_word(self, word):
        return len(self.df[self.df['Angielski'] == word]) == 1

    def ret_ang(self, df_tmp):
        return df_tmp['Angielski']

    def ret_pol(self, df_tmp):
        return df_tmp['Polski']

    def return_polish_word_from_row(self, row):
        return row['Polski'].values[0]

    def return_english_word_from_row(self, row):
        return row['Angielski'].values[0]
