
class TraceSummary:

    # LOCAL
    frequency = 0.0
    amplitude = 0.0
    peak_to_peak_interval = 0.0
    peak_to_peak_variance = 0.0

    def __init__(self, frequency, amplitude, peak_to_peak_interval, peak_to_peak_variance):
        self.frequency = frequency
        self.amplitude = amplitude
        self.peak_to_peak_interval = peak_to_peak_interval
        self.peak_to_peak_variance = peak_to_peak_variance


    def get_array(self):
        return [self.frequency, self.amplitude, self.peak_to_peak_interval, self.peak_to_peak_variance]