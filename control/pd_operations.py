import pandas as pd


def transform_df(df: pd.DataFrame, text: str) -> pd.DataFrame:
    return df[df.Angielski.str.contains(text) | df.Polski.str.contains(text)]


def return_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path)
