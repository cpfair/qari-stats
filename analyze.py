from __future__ import division
from collections import namedtuple
import array
import json
import multiprocessing
import numpy as np
import os
import subprocess
import sys
import wave

AnalysisResult = namedtuple("AnalysisResult", "register time")


def analyze_wav(wavfn):
    # The recordings have all kind of high-frequency noise.
    # So we only look for the peak in this frequency range.
    SPEECH_FREQ_MIN = 80
    SPEECH_FREQ_MAX = 200
    SPEECH_VAD_FS_FLOOR = 0.02
    wav_file = wave.open(wavfn, 'r')
    frame_rate = wav_file.getframerate()
    window_size = 1 * frame_rate  # Process in 1 second windows.
    freq_samples = []
    freqs = None
    while True:
        # Some of the WAV files are 1+ GB, can't load the entire thing at once.
        # (can you memory-map files in Python?)
        data = wav_file.readframes(window_size)
        if not data:
            break
        data = array.array("h", data)
        data = np.array(data)

        # Drop silent frames with the world's cheapest VAD.
        avg_amplitude = sum((abs(x) for x in data)) / len(data)
        # We assume 16-bit signed samples.
        if avg_amplitude < 32768 * SPEECH_VAD_FS_FLOOR:
            continue

        # Compute FFT and pick the peak in our desired range.
        w = np.fft.fft(data)
        if freqs is None:
            freqs = np.fft.fftfreq(len(w))
            min_idx = next(iter(i for i, f in enumerate(freqs) if f * frame_rate > SPEECH_FREQ_MIN))
            max_idx = next(iter(i for i, f in enumerate(freqs) if f * frame_rate > SPEECH_FREQ_MAX))
        idx = np.argmax(np.abs(w[min_idx:max_idx])) + min_idx
        peak_freq = freqs[idx]
        freq_in_hertz = abs(peak_freq * frame_rate)
        freq_samples.append(freq_in_hertz)
    average_freq = sum(freq_samples) / len(freq_samples)
    wav_file.close()
    return AnalysisResult(average_freq, len(freq_samples))


def handle_file(fn):
    # Prepare WAV file. if required.
    if fn.endswith(".wav"):
        wavfn = fn
    else:
        path_base = os.path.dirname(fn)
        wavfn = os.path.join(path_base, "wav", "%s.wav" % os.path.basename(fn).split(".")[0])
        if not os.path.exists(wavfn):
            if not os.path.exists(os.path.join(path_base, "wav")):
                os.mkdir(os.path.join(path_base, "wav"))
            # We use only the left channel, since some recordings have the L and R channels offset by 1/2 wavelength
            # ...so mixing them down results in near silence.
            subprocess.check_call(
                ["ffmpeg",
                 "-v", "0",
                 "-nostats",
                 "-hide_banner",
                 "-y",
                 "-i", fn,
                 "-ar", "16000",
                 "-map_channel", "0.0.0", # Only left channel.
                 wavfn], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return analyze_wav(wavfn)


files = sys.argv[1:]
res = multiprocessing.Pool().map(handle_file, files)

qari_stats = {}
for fn, freq in sorted(zip(files, res), key=lambda x: x[1][1]):
    qari_key = os.path.basename(fn).split(".")[0]
    qari_stats[qari_key] = {
        "register": freq.register,
        "time": freq.time,
    }

json.dump(qari_stats, sys.stdout)
