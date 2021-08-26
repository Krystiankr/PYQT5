import pandas as pd


class Data:
    def __init__(self):
        self.df = pd.read_csv('Data.csv')

    def print_df(self):
        print(self.df)

    def len_df(self):
        return len(self.df)

    def df_return(self):
        return self.df

    def df_random_return(self):
        return self.df[self.df['Frequency'] == self.df['Frequency'].min()]

    def len_random(self):
        return len(self.df[self.df['Frequency'] == self.df['Frequency'].min()])

    def reset_df(self):
        self.df = pd.read_csv('Data.csv')

    def sample_row(self):
        return self.df[self.df['Frequency'] == self.df['Frequency'].min()].sample()

    def increase_frequency(self, word):
        self.df.at[self.df[self.df['Angielski'] == word].index[0], 'Frequency'] += 1

    def add_new_word(self, ang, pol):
        if not self.is_there_word(ang):
            self.df.loc[self.df.index.max() + 1] = [ang] + [pol] + [0]
            return "Added new word"
        else:
            return "The word already exists"

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
