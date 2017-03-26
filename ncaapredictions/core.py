import os
import pandas as pd
from sklearn import cross_validation, linear_model

from .io import write_results
from .ncaa import build_season_data, predict_winner


def command(year, data_path, output_path):
    print("Generating results for " + year + ".")

    # Setting up globals.
    submission_data = []
    prediction_year = int(year)

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
    seeds = pd.read_csv(os.path.join(data_path, 'TourneySeeds.csv'))
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

    write_results(output_path, data_path, submission_data)

