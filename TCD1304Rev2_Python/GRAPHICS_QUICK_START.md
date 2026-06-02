# Quick Start: Graphics Display

You now have full graphics support! Here's what changed:

## What's New

✅ **Graphics support added to LightMeter**
- New parameter: `graphics=True` enables real-time visualization
- Example: `python example_light_graphics.py`
- Warnings are suppressed automatically

## How to Use

### Option 1: Graphics Display (Recommended for Learning)

```bash
python example_light_graphics.py
```

Shows a live updating graph of light intensity across all pixels.

### Option 2: Text Only (Simpler)

```bash
python example_light_measurement.py
```

Shows just the statistics without graphics.

### Option 3: In Your Code

```python
from light_meter import LightMeter

# WITH graphics
meter = LightMeter('/dev/ttyACM1', graphics=True)

# WITHOUT graphics
meter = LightMeter('/dev/ttyACM1', graphics=False)
```

## Files Added

| File | Purpose |
|------|---------|
| `example_light_graphics.py` | **NEW**: Complete graphics example |
| `GRAPHICS_GUIDE.md` | **NEW**: Detailed graphics documentation |
| `light_meter.py` | Updated: Added `graphics` parameter |
| `example_light_measurement.py` | Updated: Added warning suppression |

## Understanding the Warnings

You may see this warning:
```
UserWarning: Treat the new Tool classes introduced in v1.5 as experimental
```

**This is NOT an error.** It's just matplotlib notifying that some features are still experimental. The graphics work perfectly fine - we automatically suppress the warning.

## What the Graph Shows

The real-time graph displays:
- **X-axis**: Pixel position (0-3668)
- **Y-axis**: Light intensity (0-1)
- **Live updates**: Every 200ms
- **Each line**: Full pixel profile across sensor

## Examples

### Show Graphics with Stats

```python
from light_meter import LightMeter
import time

meter = LightMeter('/dev/ttyACM1', graphics=True)

for i in range(5):
    stats = meter.get_statistics()
    print(f"Light: {stats['mean']*100:.1f}%")
    time.sleep(1)

meter.close()
```

### Find Brightest Spot

```python
from light_meter import LightMeter
import numpy as np

meter = LightMeter('/dev/ttyACM1', graphics=True)
pixels = meter.get_normalized_pixels()
brightest = np.argmax(pixels)
print(f"Brightest pixel: {brightest} ({pixels[brightest]:.2f})")
meter.close()
```

## Troubleshooting

**Graph doesn't appear?**
- Make sure you pass `graphics=True`
- Check that matplotlib is working: `python -c "import matplotlib.pyplot as plt"`

**Too many warnings?**
- They're automatically suppressed in the example files
- Add this at the top of your script: `import warnings; warnings.filterwarnings('ignore')`

**Graph is slow?**
- This is normal - it's updating every 200ms with full pixel data
- Use `graphics=False` if speed is critical

## Documentation

- **Quick start**: This file (you are here)
- **Full reference**: `GRAPHICS_GUIDE.md`
- **Light meter basics**: `LIGHT_METER_GUIDE.md`
- **Controller reference**: `TCD1304Rev2_Python/` directory

## Next Steps

1. Try: `python example_light_graphics.py`
2. Read: `GRAPHICS_GUIDE.md` for more examples
3. Modify: Use the examples as templates for your code

