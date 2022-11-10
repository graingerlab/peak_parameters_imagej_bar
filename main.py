import sys
import data
import os
import pandas as pd
import functools

INPUT_PATH = sys.argv[1]
directory = ''
filter_list = []

data_objects = []
data_rows = []
trace_frequencies = []
trace_amplitudes = []
trace_ppi = []
trace_ppiv = []

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def process_files(file_directory):
    global directory
    directory = file_directory

    for file in listdir_fullpath(file_directory):
        file_path = os.fsdecode(file)

        if data.SUMMARY_NAME in file_path or \
            data.AMPLITUDES_NAME in file_path or \
            data.NORMALIZED_NAME in file_path or \
            'sort' in file_path or \
            '.DS_Store' in file_path:
            continue

        process_file(file_path)


def process_file(file_path):
    data_object = data.Data(file_path)
    data_object.process()
    data_object.plot_trace()
    data_objects.append(data_object)


def sort_data_objects():
    for file in listdir_fullpath(directory):
        file_path = os.fsdecode(file)

        if 'sort' in file_path:
            # custom sort
            with open(file_path) as f:
                contents = f.read().lower()

                global filter_list
                filter_list = contents.split(' ')
                data_objects.sort(key=functools.cmp_to_key(compare_name_filter))
                return

    # if we didn't find a file, use file_name
    data_objects.sort(key=lambda x: x.file_name, reverse=False)


def compare_name_filter(item1, item2):
    comparison = evaluate_name_filter(item1) - evaluate_name_filter(item2)

    if comparison != 0:
        return comparison
    else:
        return evaluate_value(item1, item2)


def evaluate_name_filter(data_object):
    for index, filter in enumerate(filter_list):
        if filter in data_object.file_name.lower():
            return index

    return len(filter_list)


def evaluate_value(item1, item2):
    if item1.file_value > item2.file_value:
        return 1
    if item1.file_value < item2.file_value:
        return -1

    return 0


def collate_mean_values():
    for data_object in data_objects:
        trace_frequencies.append(data_object.trace_summary.frequency)
        trace_amplitudes.append(data_object.trace_summary.amplitude)
        trace_ppi.append(data_object.trace_summary.peak_to_peak_interval)
        trace_ppiv.append(data_object.trace_summary.peak_to_peak_variance)


def normalize_mean_value(arr):
    target = arr[0]

    for i in range(len(arr)):
        arr[i] = target/arr[i]

    return arr


def normalize_mean_values():
    norm_freq = normalize_mean_value(trace_frequencies)
    norm_amplitude = normalize_mean_value(trace_amplitudes)
    norm_PPI = normalize_mean_value(trace_ppi)
    norm_PPIV = normalize_mean_value(trace_ppiv)

    for i in range(len(data_objects)):
        data_rows.append([data_objects[i].file_name, norm_freq[i], norm_amplitude[i], norm_PPI[i], norm_PPIV[i]])


def save_normalized_data():
    user_input = ''
    options = ['yes', 'no']

    print("Would you like to save the normalized data? Enter yes or no: ")

    while user_input not in options:
        user_input = input()

    columns = ['File',
               'Norm Frequency',
               'Norm Amplitude',
               'Norm PPI',
               'Norm PPIV']

    if user_input == "yes":
        normalized_data = pd.DataFrame(data_rows, columns=columns)

        output_path = os.path.join(directory, "normalized_data_summary.csv")
        normalized_data.to_csv(output_path)

        print("Finished saving normalized data")


def save_amplitude_and_summary_data():
    user_input = ''
    options = ['yes', 'no']

    print("Would you like to save the amplitude and summary data? Enter yes or no: ")

    while user_input not in options:
        user_input = input()

    if user_input == "yes":
        for data_object in data_objects:
            data_object.save()

        print("Finished saving amplitude and summary data")


if os.path.isfile(INPUT_PATH):
    process_file(INPUT_PATH)
else:
    process_files(INPUT_PATH)

sort_data_objects()
collate_mean_values()
normalize_mean_values()

save_amplitude_and_summary_data()
save_normalized_data()
