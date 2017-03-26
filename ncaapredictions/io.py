import os
import pandas as pd


def read_all_data(data_path):
    season_data = pd.read_csv(
        os.path.join(
            data_path, "RegularSeasonDetailedResults.csv"
        )
    )
    tourney_data = pd.read_csv(
        os.path.join(
            data_path, "TourneyDetailedResults.csv"
        )
    )
    return pd.concat([season_data, tourney_data])