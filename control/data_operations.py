import pandas as pd
FILEPATH = 'control/Data.csv'


class DataOperations:
    def __init__(self):
        self.df = pd.read_csv(FILEPATH, encoding='utf8')

    def sample_row(self):
        random = self.df[self.df.Frequency == self.df.Frequency.min()]
        return random.sample()

    def get_polish_word(self, row):
        return row['Polski'].values[0]

    @staticmethod
    def get_english_word(row):
        return row['Angielski'].values[0]

    def get_sample_polish(self):
        return self.get_polish_word(self.sample_row())

    def get_num_all_words(self):
        return len(self.df)

    def get_df(self):
        return self.df

    @staticmethod
    def get_numm_words_from_tmp_df(df: pd.DataFrame) -> int:
        return len(df)

    def english_cointains_word(self, word: str) -> bool:
        return self.df.Angielski.str.contains(word).any()

    def polish_cointains_word(self, word: str) -> bool:
        return self.df.Polski.str.contains(word).any()

    def get_max_index(self) -> int:
        return self.df.index.max()

    def add_row_to_end(self, row: list) -> None:
        self.df.loc[self.get_max_index() + 1] = row

    def get_min_freq(self) -> int:
        return self.df.Frequency.min()

    def get_translation(self, english_word: str) -> str:
        if self.english_cointains_word(english_word):
            return self.df[self.df.Angielski.str.contains(english_word)].Polski.values[0]

    def get_translation_from_pl(self, polish_word: str) -> str:
        if self.polish_cointains_word(polish_word):
            return self.df[self.df.Polski.str.contains(polish_word)].Angielski.values[0]

    def add_new_word(self, *, english_word, polish_word):
        if not self.english_cointains_word(english_word):
            self.add_row_to_end(
                [english_word, polish_word, self.get_min_freq(), 0, 0])
            self.save_actual_df_and_reload()
            return f"Added new word [{english_word}]:[{polish_word}]"
        return f"The word already exists [{english_word}]:[{self.get_translation(english_word)}]"

    def save_actual_df_and_reload(self):
        self.get_df().to_csv(FILEPATH, index=False, encoding='utf-8-sig')

    def reload_df(self) -> None:
        self.df = pd.read_csv(FILEPATH, encoding='utf8')
