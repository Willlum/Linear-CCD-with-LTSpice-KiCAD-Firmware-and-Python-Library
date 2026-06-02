# Light Intensity Meter Guide

Simplified interface for measuring normalized light intensity with the TCD1304 CCD sensor.

## What It Does

The `LightMeter` class provides a simplified interface to measure light intensity without the overhead of spectrographic features like wavelength calibration and time-series analysis.

**Key features:**
- Normalized light output (0-1 scale)
- Simplified API (no spectrograph complexity)
- No graphics windows or logging
- Fast and lightweight
- Statistical analysis of light levels

---

## Basic Usage

### Simple Measurement

```python
from light_meter import LightMeter

# Connect to device
meter = LightMeter('/dev/ttyACM1')

# Get average light intensity (0.0 = dark, 1.0 = full brightness)
intensity = meter.get_light_intensity()
print(f"Light: {intensity:.4f}")

# Close connection
meter.close()
```

### Get Statistics

```python
meter = LightMeter('/dev/ttyACM1')

stats = meter.get_statistics()
print(f"Average:  {stats['mean']:.4f}")
print(f"Min:      {stats['min']:.4f}")
print(f"Max:      {stats['max']:.4f}")
print(f"StdDev:   {stats['std']:.4f}")
print(f"Total:    {stats['sum']:.1f}")

meter.close()
```

### Real-time Monitoring

```python
from light_meter import LightMeter
import time

meter = LightMeter('/dev/ttyACM1')

try:
    while True:
        intensity = meter.get_light_intensity()
        print(f"Light: {intensity*100:.1f}%")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Stopped")
finally:
    meter.close()
```

### Get Raw Pixel Data

```python
meter = LightMeter('/dev/ttyACM1')

# Get normalized pixel values (0-1 for each pixel)
pixels = meter.get_normalized_pixels()
print(f"Pixels shape: {pixels.shape}")  # (3668,) for TCD1304

# Get statistics per pixel
brightest_pixel = pixels.max()
darkest_pixel = pixels.min()

meter.close()
```

---

## API Reference

### LightMeter Class

#### `__init__(port, debug=False)`
Initialize the light meter.

**Parameters:**
- `port` (str): Serial port (e.g., '/dev/ttyACM1')
- `debug` (bool): Enable debug output

**Example:**
```python
meter = LightMeter('/dev/ttyACM1')
```

#### `get_light_intensity()`
Get normalized average light intensity.

**Returns:**
- float: Light intensity (0.0 = dark, 1.0 = full brightness)

**Example:**
```python
intensity = meter.get_light_intensity()  # Returns 0.5432
```

#### `get_pixel_data()`
Get raw voltage data for all pixels.

**Returns:**
- numpy array: Voltage for each pixel (0 to vfs volts)

**Example:**
```python
data = meter.get_pixel_data()
print(f"Min voltage: {data.min():.3f}V")
print(f"Max voltage: {data.max():.3f}V")
```

#### `get_normalized_pixels()`
Get normalized (0-1) intensity for each pixel.

**Returns:**
- numpy array: Normalized intensity (0.0 to 1.0 for each pixel)

**Example:**
```python
normalized = meter.get_normalized_pixels()
bright_pixels = normalized > 0.8  # Find bright pixels
```

#### `get_statistics()`
Get comprehensive light statistics.

**Returns:**
- dict: Statistics dictionary with keys:
  - `mean`: Average normalized intensity
  - `min`: Minimum pixel value
  - `max`: Maximum pixel value
  - `std`: Standard deviation
  - `sum`: Total light (sum of all pixels)

**Example:**
```python
stats = meter.get_statistics()
if stats['mean'] > 0.5:
    print("Bright conditions")
else:
    print("Dark conditions")
```

#### `close()`
Close the meter and release resources.

**Example:**
```python
meter.close()
```

---

## Device Specifications

**TCD1304 Sensor:**
- Pixels: 3,668
- Dark pixels: 13 (for baseline)
- Bit depth: 12-bit (0-4095)
- Voltage range: 0.825V (configurable)
- Voltage per bit: 0.0002015V

---

## Examples

### Example 1: Simple Light Meter

```python
from light_meter import LightMeter

meter = LightMeter('/dev/ttyACM1')
stats = meter.get_statistics()

print(f"Ambient Light: {stats['mean']*100:.1f}%")
print(f"Bright: {stats['max']*100:.1f}% | Dark: {stats['min']*100:.1f}%")

meter.close()
```

### Example 2: Monitor Light Changes

```python
from light_meter import LightMeter
import time

meter = LightMeter('/dev/ttyACM1')
prev_intensity = 0

try:
    while True:
        current = meter.get_light_intensity()
        change = (current - prev_intensity) * 100
        
        if abs(change) > 5:
            print(f"Light changed: {change:+.1f}%")
        
        prev_intensity = current
        time.sleep(1)
finally:
    meter.close()
```

### Example 3: Detect Motion/Changes

```python
from light_meter import LightMeter
import time

meter = LightMeter('/dev/ttyACM1')
baseline_pixels = meter.get_normalized_pixels()

print("Monitoring for changes...")

try:
    while True:
        current_pixels = meter.get_normalized_pixels()
        
        # Compare pixel variance
        diff = abs(current_pixels - baseline_pixels).mean()
        
        if diff > 0.05:  # 5% change threshold
            print(f"Change detected! Diff: {diff*100:.1f}%")
            baseline_pixels = current_pixels
        
        time.sleep(0.5)
finally:
    meter.close()
```

---

## Data Flow

```
Hardware Device (/dev/ttyACM1)
         ↓
    Serial Data (12-bit values)
         ↓
    LccdController (reader thread)
    - Converts to voltage (multiply by vperbit)
    - Removes baseline (dark pixels)
    - Puts in queue
         ↓
    LightMeter
    - Gets data from queue
    - Normalizes (divide by vfs)
    - Returns 0-1 range
         ↓
    Your Application
```

---

## Normalization Explained

The light intensity is normalized to a 0-1 scale:

```
Raw pixel value (0-4095 for 12-bit)
         ↓
Multiply by vperbit = Voltage (0-0.825V)
         ↓
Divide by vfs = Normalized (0-1)

Formula: normalized = (raw * vperbit) / vfs
```

**Interpretation:**
- 0.0 = Completely dark (0V)
- 0.5 = 50% brightness (0.4125V)
- 1.0 = Full brightness (0.825V)

---

## Troubleshooting

### "No such file or directory: /dev/ttyACM1"
Device not found or wrong port. Check:
```bash
ls /dev/tty*
```

### "could not open port"
Permission denied. Fix with:
```bash
sudo usermod -a -G dialout $USER
newgrp dialout
```

### "ValueError: configuration not found"
Device communication issue. Try:
- Reconnect USB cable
- Check baud rate
- Power cycle device

---

## Comparison: LightMeter vs Full Controller

| Feature | LightMeter | Full Controller |
|---------|-----------|-----------------|
| Light measurement | ✅ | ✅ |
| Spectrograph | ❌ | ✅ |
| Time-series | ❌ | ✅ |
| Graphics window | ❌ | ✅ |
| Learning curve | ⭐ | ⭐⭐⭐ |
| Code complexity | Simple | Advanced |

**Use LightMeter when:** You only need light intensity measurements
**Use Full Controller when:** You need wavelength calibration or time-series analysis

---

## Next Steps

- See `example_light_measurement.py` for a complete working example
- Check `data_models.py` for lower-level data access
- Use `TCD1304Rev2Controller.py` for advanced features

