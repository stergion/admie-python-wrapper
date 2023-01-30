from pathlib import Path

import pandas as pd


def dailyEnergyBalanceAnalysis_parser(filePath: Path) -> pd.DataFrame:
    df = pd.read_excel(filePath, skiprows=20, usecols="E", header=None)
    df = df.dropna()
    df = df.set_index([pd.CategoricalIndex(['LIGNITE', 'GAS', 'HYDRO', 'RES', "IMPORTS", "TOTAL"])])
    df = df.transpose()
    df = df.set_index(pd.DatetimeIndex([filePath.name.split('_')[0]], freq='d'))
    return df
