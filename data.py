##### Script to get amplitude data (all values and average) with csv files output from VT viewer software #####

# ----------import all packages and modules------------# import in alphabetical order

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from os import path
from trace_summary import *

# GLOBALS
FILE_EXTENSION = '.csv'
FRAME_RATE = 20
SUMMARY_NAME = 'summary_'
AMPLITUDES_NAME = 'amplitudes_'
NORMALIZED_NAME = 'normalized_'

class Data:

    # LOCAL
    file_directory = ''
    file_path = ''
    file_name = ''
    file_value = 0.0

    summary_output_file_name = ''
    amplitudes_output_file_name = ''
    amplitudes_output_path = ''
    summary_output_path = ''

    trace_raw_data_x = []
    trace_raw_data_y = []
    trace_maxima_x = []
    trace_maxima_y = []
    trace_minima_x = []
    trace_minima_y = []

    peak_to_peak_interval_mean = 0.0
    peak_to_peak_interval_min = 0.0
    peak_to_peak_interval_max = 0.0
    peak_to_peak_interval_stdev = 0.0
    peak_to_peak_interval_var = 0.0

    peak_freq_sec = 0.0

    trace_amplitude_parameters = None
    trace_summary = None

    def __init__(self, file_path):
        self.file_directory = path.dirname(file_path)
        self.file_path = file_path

        file_name = path.splitext(path.basename(file_path))[0]
        self.file_name = file_name
        self.file_value = self.get_file_value(file_name)

        self.summary_output_file_name = f'{SUMMARY_NAME}{self.file_name}{FILE_EXTENSION}'
        self.amplitudes_output_file_name = f"{AMPLITUDES_NAME}{self.file_name}{FILE_EXTENSION}"
        self.amplitudes_output_path = path.join(self.file_directory, self.amplitudes_output_file_name)
        self.summary_output_path = path.join(self.file_directory, self.summary_output_file_name)


    def get_file_value(self, file_name):
        output = ''.join(n for n in file_name if n.isdigit())

        if output.isdigit():
            return int(output)
        else:
            return 0.0


    def process(self):
        print(f'Processing {self.file_name}...')

        def split_and_sort_data(column_x, column_y):
            data = pd.read_csv(self.file_path, usecols=[column_x, column_y])
            data.dropna(how='any', inplace=True)
            data.sort_values(by=column_x, inplace=True, ascending=True, ignore_index=True)

            output_x = data[column_x]
            output_y = data[column_y]

            return (output_x, output_y)

        trace_raw_data = split_and_sort_data("X0", "Y0")
        self.trace_raw_data_x = trace_raw_data[0]
        self.trace_raw_data_y = trace_raw_data[1]

        trace_maxima = split_and_sort_data("X1", "Y1")
        self.trace_maxima_x = trace_maxima[0]
        self.trace_maxima_y = trace_maxima[1]

        trace_minima = split_and_sort_data("X2", "Y2")
        self.trace_minima_x = trace_minima[0]
        self.trace_minima_y = trace_minima[1]

        # ----------Delete last values of arrays------------#

        trace_maxima_is_first_element = self.trace_maxima_x[0] <= self.trace_minima_x[0]

        if trace_maxima_is_first_element:
            print("Removed first maxima", self.trace_maxima_x[0], self.trace_minima_x[0])
            index = 0
            self.trace_maxima_x.drop(self.trace_maxima_x.index[index], inplace=True)
            self.trace_maxima_y.drop(self.trace_maxima_y.index[index], inplace=True)

        trace_minima_is_last_element = self.trace_minima_x[self.trace_minima_x.size - 1] >= self.trace_maxima_x[self.trace_maxima_x.size - 1]

        if trace_minima_is_last_element:
            print("Removed last minima", self.trace_minima_x[self.trace_minima_x.size - 1], self.trace_maxima_x[self.trace_maxima_x.size - 1])
            index = self.trace_minima_x.size - 1
            self.trace_minima_x.drop(self.trace_minima_x.index[index], inplace=True)
            self.trace_minima_y.drop(self.trace_minima_y.index[index], inplace=True)

        # ----------Calculate peak frequency------------#

        total_frame_number = len(trace_raw_data[0])
        total_maxima = len(trace_maxima[0])
        total_time = (total_frame_number / FRAME_RATE)
        self.peak_freq_sec = total_maxima / total_time

        # ----------Calculate peak-peak(r-r) interval and print------------#

        div_sort_min_x_coord = trace_minima[0] / FRAME_RATE

        peak_to_peak_interval = np.diff(div_sort_min_x_coord)
        self.peak_to_peak_interval_mean = np.mean(peak_to_peak_interval)
        self.peak_to_peak_interval_min = np.min(peak_to_peak_interval)
        self.peak_to_peak_interval_max = np.max(peak_to_peak_interval)
        self.peak_to_peak_interval_stdev = np.std(peak_to_peak_interval)
        self.peak_to_peak_interval_var = np.var(peak_to_peak_interval)

        # ----------------------#

        self.trace_amplitude_parameters = self.calculate_trace_amplitude(self.trace_maxima_y, self.trace_minima_y)
        self.trace_summary = TraceSummary(self.peak_freq_sec, self.trace_amplitude_parameters[1], self.peak_to_peak_interval_mean, self.peak_to_peak_interval_var)


    def calculate_trace_amplitude(self, a, b):
        rangeAmplitude = np.subtract(a, b)
        meanAmplitude = np.mean(rangeAmplitude)
        minAmplitude = np.amin(rangeAmplitude)
        maxAmplitude = np.amax(rangeAmplitude)
        stdevAmplitude = np.std(rangeAmplitude)

        return (meanAmplitude, minAmplitude, maxAmplitude, stdevAmplitude)


    def plot_trace(self):
        # ----------Plot line graph with found peaks in plotly------------#
        trace = go.Figure()

        trace.add_trace(go.Scatter(x=self.trace_raw_data_x, y=self.trace_raw_data_y,
                                   mode='lines',
                                   name='filtered trace'))

        trace.add_trace(go.Scatter(x=self.trace_maxima_x, y=self.trace_maxima_y,
                                   mode='markers', marker=dict(size=8, color='red', symbol='cross'),
                                   name='maxima'))

        trace.add_trace(go.Scatter(x=self.trace_minima_x, y=self.trace_minima_y,
                                   mode='markers', marker=dict(size=8, color='magenta', symbol='cross'),
                                   name='minima'))

        trace.update_layout(
            title_text=f'{len(self.trace_maxima_x)} maxima and {len(self.trace_minima_x)} minima'
        )

        trace.show()


    def save(self):
        print(f'Saving {self.file_name}...')

        amplitude_data = pd.DataFrame({'amplitude': self.trace_amplitude_parameters[0]})
        amplitude_data.to_csv(self.amplitudes_output_path)

        trace_amplitude_summary_output = (self.trace_amplitude_parameters[1], self.trace_amplitude_parameters[2], self.trace_amplitude_parameters[3], self.trace_amplitude_parameters[4])
        combined_summary_data = np.array([[self.peak_freq_sec, 0, 0, 0], trace_amplitude_summary_output,
                                          [self.peak_to_peak_interval_mean, self.peak_to_peak_interval_min,
                                           self.peak_to_peak_interval_max, self.peak_to_peak_interval_stdev],
                                          [self.peak_to_peak_interval_var, 0, 0, 0]])

        index_values = ['Frequency(contractions/min)', 'Amplitude(microns)', 'Peak-Peak Interval (sec)',
                        'Peak-Peak Interval Variance (sec)']
        column_values = ['mean', 'min', 'max', 'stdev']
        summaryDf = pd.DataFrame(data=combined_summary_data,
                                 index=index_values,
                                 columns=column_values)

        # ----------Generate a new csv file and save calculated amplitude array data into it------------#
        summaryDf.to_csv(self.summary_output_path)
