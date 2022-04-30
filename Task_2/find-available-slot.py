import pandas as pd
import numpy as np
import os
import datetime
from itertools import combinations
import argparse

def find_available_slot(path_dict, duration, minumum_people):
    calendar_dict = {}
    path_dict = str(path_dict).strip('/')
    arr = os.listdir(path_dict)

    for person in arr:
        person_list = []
        with open(path_dict + '/' + str(person)) as f:
            for line in f:
                person_list.append(line.strip())
            calendar_dict[person[:-4]] = person_list

    max_date = datetime.date(1000, 1, 1)
    min_date = datetime.date(9999, 12, 31)
    for date in [value for values in calendar_dict.values() for value in values]:
        if len(date) == 41:
            date = date[22:32]
        date = datetime.date.fromisoformat(date)
        if date > max_date:
            max_date = date
        if date < min_date:
            min_date = date

    return_date = max_date
    min_date = datetime.datetime.fromisoformat(str(min_date) + ' 00:00:00')
    max_date = datetime.datetime.fromisoformat(str(max_date) + ' 23:59:59')
    delta = max_date - min_date + datetime.timedelta(days=1)
    m = int(delta.seconds / 60 * delta.days) + 1
    calendar_matrix = []
    for i in range(m):
        i_date = min_date + datetime.timedelta(minutes=i)
        calendar_matrix.append([i_date] + [0]*len(arr))
        for idx, person in enumerate(calendar_dict.items(), 1):
            for date in person[1]:
                if len(date) == 10:
                    start_date = datetime.datetime.fromisoformat(str(date) + ' 00:00:00')
                    end_date = datetime.datetime.fromisoformat(str(date) + ' 23:59:59')
                    if start_date <= i_date <= end_date:
                        calendar_matrix[i][idx] = 1
                elif len(date) == 41:
                    start_date = datetime.datetime.fromisoformat(str(date[:19]))
                    end_date = datetime.datetime.fromisoformat(str(date[22:]))
                    if start_date <= i_date <= end_date:
                        calendar_matrix[i][idx] = 1

    calendar_df = pd.DataFrame(calendar_matrix, columns=['date']+list(calendar_dict.keys()))

    window_matrix = np.zeros((duration, minumum_people), dtype=int)

    calendar_array = np.array(calendar_df.iloc[:, 1:].values.tolist())

    for lvl in range(calendar_df.shape[0]):
        if minumum_people == len(arr):
            if lvl >= calendar_array.shape[0] - duration:
                if np.all(calendar_array[lvl:, :] == window_matrix[calendar_array.shape[0] - lvl:, :]):
                    return calendar_df.iloc[lvl, 0]
            else:
                if np.all(calendar_array[lvl:lvl+duration, :] == window_matrix):
                    return calendar_df.iloc[lvl, 0]
        else:
            for comb in list(combinations(range(1, calendar_df.shape[1]), minumum_people)):
                calendar_array_cut = np.array(calendar_df.iloc[:, list(comb)].values.tolist())
                if lvl >= calendar_array_cut.shape[0] - duration:
                    if np.all(calendar_array_cut[lvl:, :] == window_matrix[calendar_array_cut.shape[0] - lvl:, :]):
                        return calendar_df.iloc[lvl, 0]
                else:
                    if np.all(calendar_array_cut[lvl:lvl+duration, :] == window_matrix):
                        return calendar_df.iloc[lvl, 0]

    return_date += datetime.timedelta(days=1)
    return datetime.datetime.fromisoformat(str(return_date) + ' 00:00:00')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--calendars")
    parser.add_argument("--duration-in-minutes")
    parser.add_argument("--minimum-people")
    args = parser.parse_args()
    config = vars(args)
    path_dict = str(config['calendars'])
    duration_in_minutes = int(config['duration_in_minutes'])
    minimum_people = int(config['minimum_people'])

    print(find_available_slot(path_dict, duration_in_minutes, minimum_people))
