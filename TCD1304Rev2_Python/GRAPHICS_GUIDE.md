# Graphics Display for Light Intensity Measurement

Real-time graphical visualization of light intensity measurements from the TCD1304 sensor.

## Overview

The graphics window displays:
- **X-axis**: Pixel position (0 to 3668 pixels)
- **Y-axis**: Normalized light intensity (0 to 1 scale)
- **Updates**: Every 200ms with new data
- **Real-time**: Shows instantaneous pixel-by-pixel light levels

## Usage

### Quick Start

```bash
python example_light_graphics.py
```

This shows a live graph of light intensity across all pixels.

### In Your Code

```python
from light_meter import LightMeter

# Create meter WITH graphics
meter = LightMeter('/dev/ttyACM1', graphics=True)

# Get measurements - graphics update automatically
stats = meter.get_statistics()
print(f"Light: {stats['mean']*100:.1f}%")

meter.close()
```

### With Both Graphics and Statistics

```python
from light_meter import LightMeter
import time

meter = LightMeter('/dev/ttyACM1', graphics=True)

try:
    for i in range(10):
        stats = meter.get_statistics()
        print(f"Measurement {i+1}: {stats['mean']*100:.1f}%")
        time.sleep(1)
finally:
    meter.close()
```

## Understanding the Graph

### What You See

The graph shows a **light intensity profile** across all pixels:

```
Intensity
1.0 |     ╱╲╱╲         <-- Bright areas
    |    ╱  ╲╱ ╲
0.5 |───╱────────╲─── <-- Medium brightness
    |  ╱          ╲
0.0 |______________╲__ <-- Dark areas
    0   1000   2000   3000   Pixel
```

### Interpreting Results

- **Flat line near 1.0**: Uniform bright light
- **Flat line near 0.0**: Dark/no light
- **Peaks and valleys**: Non-uniform illumination
- **Noise/roughness**: Random variations (sensor noise)

## Warnings (Safe to Ignore)

You may see matplotlib warnings like:

```
UserWarning: Treat the new Tool classes introduced in v1.5 as experimental
```

These are **not errors** - just matplotlib version compatibility notices. The graphics will work fine.

To suppress them, add at the top of your script:

```python
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
```

## Examples

### Example 1: Monitor Light Changes

```python
from light_meter import LightMeter
import time

meter = LightMeter('/dev/ttyACM1', graphics=True)

print("Graph will update as light changes...")
print("Try shining a flashlight on the sensor!\n")

try:
    while True:
        stats = meter.get_statistics()
        print(f"Average light: {stats['mean']*100:.1f}%")
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    meter.close()
```

### Example 2: Find Brightest Pixel

```python
from light_meter import LightMeter
import numpy as np

meter = LightMeter('/dev/ttyACM1', graphics=True)

pixels = meter.get_normalized_pixels()
brightest_pixel = np.argmax(pixels)
brightest_value = pixels[brightest_pixel]

print(f"Brightest pixel: #{brightest_pixel}")
print(f"Brightness level: {brightest_value:.4f}")

meter.close()
```

### Example 3: Detect Shadows

```python
from light_meter import LightMeter
import time

meter = LightMeter('/dev/ttyACM1', graphics=True)

baseline = meter.get_statistics()['mean']
print(f"Baseline light: {baseline*100:.1f}%\n")

try:
    while True:
        current = meter.get_statistics()['mean']
        change = (current - baseline) * 100
        
        if change < -5:  # More than 5% darker
            print(f"Shadow detected! Light decreased by {-change:.1f}%")
        elif change > 5:  # More than 5% brighter
            print(f"Bright! Light increased by {change:.1f}%")
        
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    meter.close()
```

## Files

- **`light_meter.py`** - Main class with `graphics` parameter
- **`example_light_graphics.py`** - Complete working example with graphics
- **`example_light_measurement.py`** - Simple example without graphics

## Comparison

| Feature | With Graphics | Without Graphics |
|---------|---------------|------------------|
| Visual display | ✅ Real-time graph | ❌ No |
| Performance | Slightly slower | Faster |
| Terminal output | ✅ Statistics | ✅ Statistics |
| CPU usage | Higher | Lower |
| Memory | More | Less |
| Learning curve | Easy | Easiest |

## Tips

1. **Full screen**: Click the maximize button on the graph window for better view
2. **Navigate**: Use arrow keys (← →) to move through time history (if enabled)
3. **Zoom**: Use the zoom tool in the matplotlib toolbar
4. **Pan**: Use the pan tool to move around the plot
5. **Home**: Click "home" button to reset view

## Troubleshooting

### Graph Not Showing
- Make sure X11 forwarding is enabled if using SSH
- Check your matplotlib backend: `python -c "import matplotlib; print(matplotlib.get_backend())"`

### Graph Freezes
- Device not sending data - check serial connection
- Click graph to focus it, or wait for data

### Warnings About Toolbar
- These are harmless matplotlib version compatibility warnings
- Suppress with: `warnings.filterwarnings('ignore')`

## Next Steps

See main documentation:
- `LIGHT_METER_GUIDE.md` - Full reference
- `example_light_measurement.py` - Text-only measurements
- `TCD1304Rev2_Python/` - Full controller documentation

