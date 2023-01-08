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
    def get_english_poland_col_names() -> list[str]:
        return ['Polski', 'Angielski']

    def get_item_by(self, x: int, y: int) -> str:
        return str(self.df.iloc[x, y])

    def get_word_id_by(self, english_word: str) -> int:
        mask = self.df["Angielski"].str.match(english_word)
        index = self.df[mask].index[0]
        return index

    @staticmethod
    def get_english_word(row):
        return row['Angielski'].values[0]

    def get_sample_polish(self):
        return self.get_polish_word(self.sample_row())

    def get_num_all_words(self):
        return len(self.df)

    def get_df(self):
        return self.df

    def df_len(self):
        return len(self.df)

    @staticmethod
    def get_numm_words_from_tmp_df(df: pd.DataFrame) -> int:
        return len(df)

    def english_cointains_word(self, word: str) -> bool:
        return len(self.df[self.df.Angielski == word]) != 0
        # return self.df.Angielski.str.match(word).any()

    def polish_cointains_word(self, word: str) -> bool:
        return self.df.Polski.str.match(word).any()

    def get_max_index(self) -> int:
        return self.df.index.max()

    def add_row_to_end(self, row: list) -> None:
        self.df.loc[self.get_max_index() + 1] = row

    def get_min_freq(self) -> int:
        return self.df.Frequency.min()

    def get_translation(self, english_word: str) -> str:
        if self.english_cointains_word(english_word):
            return self.df[self.df.Angielski.str.match(english_word)].Polski.values[0]

    def get_translation_from_pl(self, polish_word: str) -> str:
        if self.polish_cointains_word(polish_word):
            return self.df[self.df.Polski.str.match(polish_word)].Angielski.values[0]

    def add_new_word(self, *, english_word, polish_word):
        if not self.english_cointains_word(english_word):
            self.add_row_to_end(
                [english_word, polish_word, self.get_min_freq(), 0, 0])
            self.save_actual_df_and_reload()
            return f"Added new word [{english_word}]:[{polish_word}]"
        return f"The word already exists [{english_word}]:[{self.get_translation(english_word)}]"

    def delete_word_by(self, *, english_word):
        if not self.english_cointains_word(english_word):
            return f"The word already not exists [{english_word}]"
        drop_index = self.get_word_id_by(english_word)
        self.df.drop(index=drop_index, inplace=True)
        self.save_actual_df_and_reload()
        return f"Word [{english_word}] has been deleted."

    def save_actual_df_and_reload(self):
        self.get_df().to_csv(FILEPATH, index=False, encoding='utf-8-sig')

    def reload_df(self) -> None:
        self.df = pd.read_csv(FILEPATH, encoding='utf8')

    def get_english_index(self, english_word: str) -> int:
        return list(self.df[self.df.Angielski.str.match(english_word)].Polski.index)[0]

    def increase_frequency(self, index: int) -> None:
        self.df.at[index, 'Frequency'] += 1
