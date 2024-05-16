import numpy as np
import sounddevice as sd
from scipy.signal import spectrogram
import sys
import shutil
import time

# Constants
SAMPLE_RATE = 16000  # Sample rate in Hz
NFFT = 512  # Length of the FFT window
OVERLAP = NFFT // 2  # Overlap between windows
UPDATE_INTERVAL = 0.05  # Update interval in seconds (configurable)
MAX_WIDTH = 256  # Maximum width constraint

# Unicode block elements for better vertical resolution
UNICODE_BLOCKS = np.array([" ", "░", "▒", "▓", "█"])

# Detailed rainbow ANSI color codes
ANSI_COLORS = [
    "\033[35m",  # Violet
    "\033[34m",  # Blue
    "\033[94m",  # Light Blue
    "\033[36m",  # Cyan
    "\033[32m",  # Green
    "\033[33m",  # Yellow
    "\033[91m",  # Light Red
    "\033[31m",  # Red
    "\033[31;1m" # Bright Red
]

def get_console_width():
    return min(shutil.get_terminal_size().columns, MAX_WIDTH)

def plot_unicode_row(Sxx_mapped):
    color_row = []
    for value in Sxx_mapped:
        char = UNICODE_BLOCKS[value]
        color = ANSI_COLORS[value * (len(ANSI_COLORS) - 1) // (len(UNICODE_BLOCKS) - 1)]
        color_row.append(f"{color}{char}\033[0m")

    print("".join(color_row)[5:])  # Trim the first five characters

def process_audio(indata):
    console_width = get_console_width()  # Fit to full console width, but respect max width
    console_width = max(console_width, 12)  # Ensure there is a minimum width, adjusted to account for trimming

    f, t, Sxx = spectrogram(indata[:, 0], fs=SAMPLE_RATE, nperseg=NFFT, noverlap=OVERLAP)
    Sxx_dB = 10 * np.log10(Sxx + 1e-10)  # Adding a small number to avoid log(0)
    Sxx_scaled = (Sxx_dB - np.min(Sxx_dB)) / (np.max(Sxx_dB) - np.min(Sxx_dB))  # Normalize to 0-1
    Sxx_mapped = (Sxx_scaled.mean(axis=1) * (len(UNICODE_BLOCKS) - 1)).astype(int)

    step = max(1, len(Sxx_mapped) // (console_width - 5))  # Determine step to fit the width, minus 5 for trimming
    if step < 1:
        step = 1
    Sxx_mapped = Sxx_mapped[::step]

    plot_unicode_row(Sxx_mapped[:console_width - 5])  # Ensure the output fits the width

last_update_time = time.time()

def callback(indata, frames, ctime, status):
    global last_update_time
    if status:
        print(status, file=sys.stderr)

    if time.time() - last_update_time >= UPDATE_INTERVAL:
        process_audio(indata)
        last_update_time = time.time()

# Capture audio from the microphone with increased buffer size
with sd.InputStream(channels=1, samplerate=SAMPLE_RATE, blocksize=NFFT, callback=callback):
    print("Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        print("Stopped.")
