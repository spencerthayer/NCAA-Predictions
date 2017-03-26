# Define dependencies.
import csv
from collections import defaultdict
import os
import pandas as pd
from sklearn import cross_validation, linear_model
import time

from .ncaa import build_season_data, predict_winner, build_team_dict

def command(year, data_path):
    print("Generating results for " + year + ".")

    # Setting up globals.
    time_string = time.strftime("%y%m%d-%H%M%S", time.localtime())
    submission_data = []
    prediction_year = int(year)
    folder = 'data'

    # Build the working data.
    X, y, team_elos, team_stats = build_season_data(data_path)

    # Fit the model.
    print("Fitting on %d samples." % len(X))

    model = linear_model.LogisticRegression()

    # Check accuracy.
    print("Checking accuracy with cross-validation:")
    print(cross_validation.cross_val_score(
        model, X, y, cv=10, scoring='accuracy', n_jobs=-1
    ).mean())

    model.fit(X, y)

    # Now predict tournament matchups.
    print("Getting teams.")
    seeds = pd.read_csv(folder + '/TourneySeeds.csv')
    # for i in range for year:
    tourney_teams = []
    for index, row in seeds.iterrows():
        if row['Season'] == prediction_year:
            tourney_teams.append(row['Team'])

    # Build our prediction of every matchup.
    print("Predicting matchups.")
    tourney_teams.sort()
    for team_1 in tourney_teams:
        for team_2 in tourney_teams:
            if team_1 < team_2:
                prediction = predict_winner(
                    team_1, team_2, model, prediction_year, team_elos)
                label = str(prediction_year) + '_' + str(team_1) + '_' + \
                        str(team_2)
                submission_data.append([label, prediction[0][0]])

    # Write the results.
    print("Writing %d results." % len(submission_data))
    if not os.path.isdir("results"):
        os.mkdir("results")
    with open('results/submission.' + time_string + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'pred'])
        writer.writerows(submission_data)

    # Now so that we can use this to fill out a bracket, create a readable
    #  version.
    print("Outputting readable results.")
    team_id_map = build_team_dict(folder)
    readable = []
    less_readable = []  # A version that's easy to look up.
    for pred in submission_data:
        parts = pred[0].split('_')
        less_readable.append(
            [team_id_map[int(parts[1])], team_id_map[int(parts[2])], pred[1]])
        # Order them properly.
        if pred[1] > 0.5:
            winning = int(parts[1])
            losing = int(parts[2])
            proba = pred[1]
        else:
            winning = int(parts[2])
            losing = int(parts[1])
            proba = 1 - pred[1]
        readable.append(
            [
                '%s beats %s: %f' %
                (team_id_map[winning], team_id_map[losing], proba)
            ]
        )
    with open('results/predictions.' + time_string + '.txt', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(readable)
    with open('results/predictions.' + time_string + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(less_readable)

