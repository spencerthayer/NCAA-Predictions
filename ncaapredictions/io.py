import csv
import os
import pandas as pd
import psutil
import time

from .ncaa import build_team_dict


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


def write_results(output_path, data_path, submission_data):
    p = psutil.Process(os.getpid())
    time_string = time.strftime("%Y%m%d-%H%M",
                                time.localtime(p.create_time()))

    # Write the results.
    print("Writing %d results." % len(submission_data))

    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    submission_filename = "submission-{}.csv".format(time_string)
    submission_path = os.path.join(output_path, submission_filename)
    # TODO: change to pandas
    with open(submission_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'pred'])
        writer.writerows(submission_data)

    # Now so that we can use this to fill out a bracket, create a readable
    #  version.
    print("Outputting readable results.")
    readable = []
    less_readable = []  # A version that's easy to look up.
    team_id_map = build_team_dict(data_path)
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
    readable_txt_filename = "predictions-{}.txt".format(time_string)
    readable_txt_path = os.path.join(output_path, readable_txt_filename)
    with open(readable_txt_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(readable)

    readable_csv_filename = "predictions-{}.csv".format(time_string)
    readable_csv_path = os.path.join(output_path, readable_csv_filename)
    with open(readable_csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(less_readable)
