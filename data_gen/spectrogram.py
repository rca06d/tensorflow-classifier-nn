import numpy as np
from scipy import signal as scipy_signal

# this breaks the spectrogram up and keeps it from blowing up memory since i only have 16 gigs... :(
def spectrogram(signal, size=64, sample_rate=11025):
	signal_length = len(signal)
	segment_length = 1000000
	stride_length = segment_length - (size - 1)
	i = 0

	padded_signal = np.pad(signal, [[size, 0]], mode='constant')
	padded_signal_length = len(padded_signal)

	stft_segments = []

	while i + segment_length < padded_signal_length:
		segment = padded_signal[i:i + segment_length]
		_, _, spec = scipy_signal.spectrogram(segment, sample_rate, nperseg=size, noverlap=size-1, mode='magnitude')
		stft_segments.append(spec.transpose())
		i += stride_length

	final_segment = padded_signal[i:]

	_, _, spec = scipy_signal.spectrogram(final_segment, sample_rate, nperseg=size, noverlap=size-1, mode='magnitude')
	stft_segments.append(spec.transpose())

	return np.concatenate(stft_segments)[:signal_length]