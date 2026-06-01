import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Parameters
# -----------------------------
np.random.seed(0)

n_points = 3500
rect_width1 = 400
rect_width2 = 550
gap_width = 300
amplitude = 1.0
noise_std = 0.02
start_index = 600
slope_width = 60

# -----------------------------
# Create noisy baseline
# -----------------------------
signal = np.random.normal(0, noise_std, n_points)

# -----------------------------
# First rectangle (right edge sloped)
# -----------------------------
r1_start = start_index
r1_end = r1_start + rect_width1
signal[r1_start : r1_end - slope_width] += amplitude
ramp_down = np.linspace(amplitude, 0, slope_width)
signal[r1_end - slope_width : r1_end] += ramp_down
r2_start = r1_end + gap_width
r2_end = r2_start + rect_width2
ramp_up = np.linspace(0, amplitude, slope_width)
signal[r2_start : r2_start + slope_width] += ramp_up
signal[r2_start + slope_width : r2_end] += amplitude

from scipy.signal import find_peaks

peaks, properties = find_peaks(
    signal,
    prominence=0.4
)

fraction = 0.85
peak_heights = signal[peaks]
target_level_max = fraction * peak_heights

def crossing_position(x, y, level, direction=1):
    i = x
    while 0 <= i + direction < len(y):
        if (y[i] - level) * (y[i + direction] - level) <= 0:
            # Linear interpolation
            y1, y2 = y[i], y[i + direction]
            return i + (level - y1) / (y2 - y1)
        i += direction
    return None

left_peak, right_peak = peaks
left_edge_max = crossing_position(
    left_peak,
    signal,
    target_level_max[0],
    direction=1
)

right_edge_max = crossing_position(
    right_peak,
    signal,
    target_level_max[1],
    direction=-1
)

gap_width = right_edge_max - left_edge_max
mm_per_pixel = 0.000008
gap_mm = gap_width * mm_per_pixel
signal_floor = signal[int(np.round(left_edge_max)):int(np.round(right_edge_max))]

target_level_min = signal_floor.min()
min_val = abs(signal_floor.min())
min_indices = np.where(signal_floor <= min_val)[0].min()
left_edge_min = left_edge_max + min_indices

print("Inner wall distance:\n", gap_width)
print("Inner wall distance in mm:\n", gap_mm)
print(f"Left peak:{left_edge_max},Right peak:{right_edge_max}")
print(f"Signal floor: {signal_floor.min()}\n")


# -----------------------------
# Plot
# -----------------------------
plt.figure()
plt.plot(signal)
plt.axvline(left_edge_max, linestyle="--", color="red", linewidth=2, label="Left Inner Edge")
plt.axvline(left_edge_min, linestyle="--", color="blue", linewidth=2, label="Left Min Inner Edge")
plt.axvline(right_edge_max, linestyle="--", color="red",linewidth=2, label="Right Inner Edge")

plt.axvline((right_edge_max-left_edge_max)/2+left_edge_max, linestyle="--", color="green",linewidth=2, label="Center")
plt.title("Two Rectangular Pulses with Inner Sloped Edges")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.show()
