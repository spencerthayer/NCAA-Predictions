from collections import defaultdict
import math
import random
import pandas as pd
from tqdm import tqdm

from . import STAT_FIELDS, BASE_ELO
from .io import read_all_data


def get_k(winner_rank):
    if winner_rank < 2100:
        return 32
    elif (winner_rank >= 2100) and (winner_rank < 2400):
        return 24
    else:
        return 16


def calc_elo(winner_rank, loser_rank):
    rank_diff = winner_rank - loser_rank
    exp = (rank_diff * -1) / 400
    odds = 1 / (1 + math.pow(10, exp))

    k = get_k(winner_rank)
    new_winner_rank = round(winner_rank + (k * (1 - odds)))
    new_rank_diff = new_winner_rank - winner_rank
    new_loser_rank = loser_rank - new_rank_diff
    return new_winner_rank, new_loser_rank


def get_elo(season, team, team_elos):
    try:
        return team_elos[season][team]
    except:
        try:
            # Get the previous season's ending value.
            team_elos[season][team] = team_elos[season - 1][team]
            return team_elos[season][team]
        except:
            # Get the starter elo.
            team_elos[season][team] = BASE_ELO
            return team_elos[season][team]


def predict_winner(team_1, team_2, model, season, team_elos, team_stats):
    features = list()

    # Team 1
    features.append(get_elo(season, team_1, team_elos))
    for field in STAT_FIELDS:
        features.append(get_stat(season, team_1, field, team_stats))

    # Team 2
    features.append(get_elo(season, team_2, team_elos))
    for field in STAT_FIELDS:
        features.append(get_stat(season, team_2, field, team_stats))

    return model.predict_proba([features])


def update_stats(season, team, fields, team_stats):
    """
    This accepts some stats for a team and udpates the averages.

    First, we check if the team is in the dict yet. If it's not, we add it.
    Then, we try to check if the key has more than 5 values in it.
        If it does, we remove the first one
        Either way, we append the new one.
    If we can't check, then it doesn't exist, so we just add this.

    Later, we'll get the average of these items.
    """
    if team not in team_stats[season]:
        team_stats[season][team] = {}

    for key, value in fields.items():
        # Make sure we have the field.
        if key not in team_stats[season][team]:
            team_stats[season][team][key] = []
        # Compare the last 10 games.
        if len(team_stats[season][team][key]) >= 10:
            team_stats[season][team][key].pop()
        team_stats[season][team][key].append(value)


def get_stat(season, team, field, team_stats):
    try:
        l = team_stats[season][team][field]
        return sum(l) / float(len(l))
    except:
        return 0


def build_elo_data():
    all_data = pd.read_csv("./data/all_data.csv")
    team_elos = defaultdict(dict)

    for index, row in tqdm(all_data.iterrows()):
        season = row['Season']
        win_team = row['Wteam']
        lose_team = row['Lteam']

        winner_rank = get_elo(season, win_team, team_elos)
        loser_rank = get_elo(season, lose_team, team_elos)

        new_winner_rank, new_loser_rank = calc_elo(winner_rank, loser_rank)

        team_elos[row['Season']][row['Wteam']] = new_winner_rank
        team_elos[row['Season']][row['Lteam']] = new_loser_rank

    pd.DataFrame(
        ((_season, team, team_elos[_season][team])
         for _season in team_elos
         for team in team_elos[_season]),
        columns=["season", "team", "elo"]
    ).to_csv("./data/elo.csv", index=False)

def build_season_data(data_path):

    all_data = read_all_data(data_path)
    X = []
    y = []
    team_elos = defaultdict(dict)
    team_stats = defaultdict(dict)

    # Calculate the elo for every game for every team, each season.
    # Store the elo per season so we can retrieve their end elo
    # later in order to predict the tournaments without having to
    # inject the prediction into this loop.
    print("Building season data.")

    data = list(all_data.iterrows())[:10000]
    for index, row in tqdm(data):
        season = row['Season']
        win_team = row['Wteam']
        lose_team = row['Lteam']

        winner_rank = get_elo(season, win_team, team_elos)
        loser_rank = get_elo(season, lose_team, team_elos)

        new_winner_rank, new_loser_rank = calc_elo(winner_rank, loser_rank)

        team_elos[row['Season']][row['Wteam']] = new_winner_rank
        team_elos[row['Season']][row['Lteam']] = new_loser_rank
    #
    #
    # for index, row in tqdm(data):
    #     # Used to skip matchups where we don't have usable stats yet.
    #     skip = 0
    #
    #     # Get starter or previous elos.
    #     team_1_elo = get_elo(row['Season'], row['Wteam'], team_elos)
    #     team_2_elo = get_elo(row['Season'], row['Lteam'], team_elos)
    #
    #     # Add 100 to the home team (# taken from Nate Silver analysis.)
    #     if row['Wloc'] == 'H':
    #         team_1_elo += 100
    #     elif row['Wloc'] == 'A':
    #         team_2_elo += 100
    #
    #     # We'll create some arrays to use later.
    #     team_1_features = [team_1_elo]
    #     team_2_features = [team_2_elo]
    #
    #     # print("Building arrays out of the stats.")
    #     # Build arrays out of the stats we're tracking..
    #     for field in STAT_FIELDS:
    #         team_1_stat = get_stat(row['Season'],
    #                                row['Wteam'],
    #                                field,
    #                                team_stats)
    #         team_2_stat = get_stat(row['Season'],
    #                                row['Lteam'],
    #                                field,
    #                                team_stats)
    #         if team_1_stat is not 0 and team_2_stat is not 0:
    #             team_1_features.append(team_1_stat)
    #             team_2_features.append(team_2_stat)
    #         else:
    #             skip = 1
    #
    #     if skip == 0:  # Make sure we have stats.
    #         # Randomly select left and right and 0 or 1 so we can train
    #         # for multiple classes.
    #         if random.random() > 0.5:
    #             X.append(team_1_features + team_2_features)
    #             y.append(0)
    #         else:
    #             X.append(team_2_features + team_1_features)
    #             y.append(1)
    #
    #     # AFTER we add the current stuff to the prediction, update for
    #     # next time. Order here is key so we don't fit on data from the
    #     # same game we're trying to predict.
    #     if row['Wfta'] != 0 and row['Lfta'] != 0:
    #         stat_1_fields = {
    #             'score': row['Wscore'],
    #             'fgp': row['Wfgm'] / row['Wfga'] * 100,
    #             'fga': row['Wfga'],
    #             'fga3': row['Wfga3'],
    #             '3pp': row['Wfgm3'] / row['Wfga3'] * 100,
    #             'ftp': row['Wftm'] / row['Wfta'] * 100,
    #             'or': row['Wor'],
    #             'dr': row['Wdr'],
    #             'ast': row['Wast'],
    #             'to': row['Wto'],
    #             'stl': row['Wstl'],
    #             'blk': row['Wblk'],
    #             'pf': row['Wpf']
    #         }
    #         stat_2_fields = {
    #             'score': row['Lscore'],
    #             'fgp': row['Lfgm'] / row['Lfga'] * 100,
    #             'fga': row['Lfga'],
    #             'fga3': row['Lfga3'],
    #             '3pp': row['Lfgm3'] / row['Lfga3'] * 100,
    #             'ftp': row['Lftm'] / row['Lfta'] * 100,
    #             'or': row['Lor'],
    #             'dr': row['Ldr'],
    #             'ast': row['Last'],
    #             'to': row['Lto'],
    #             'stl': row['Lstl'],
    #             'blk': row['Lblk'],
    #             'pf': row['Lpf']
    #         }
    #         update_stats(row['Season'],
    #                      row['Wteam'],
    #                      stat_1_fields,
    #                      team_stats)
    #         update_stats(row['Season'],
    #                      row['Lteam'],
    #                      stat_2_fields,
    #                      team_stats)
    #
    #     # Now that we've added them, calc the new elo.
    #     season = row['Season']
    #     win_team = row['Wteam']
    #     lose_team = row['Lteam']
    #
    #     winner_rank = get_elo(season, win_team, team_elos)
    #     loser_rank = get_elo(season, lose_team, team_elos)
    #
    #     new_winner_rank, new_loser_rank = calc_elo(winner_rank, loser_rank)
    #
    #     team_elos[row['Season']][row['Wteam']] = new_winner_rank
    #     team_elos[row['Season']][row['Lteam']] = new_loser_rank
    #
    # return X, y, team_elos, team_stats
