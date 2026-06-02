#!/usr/bin/python

"""
Light Meter with Graphics Display

Real-time visualization of light intensity measurements.
Run this to see a live graph of light levels.
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

from light_meter import LightMeter
import time


def main():
    """Display light intensity with real-time graph."""
    
    print("="*60)
    print("Light Intensity Meter - Graphics Display")
    print("="*60)
    print("\nInitializing with graphics window...")
    
    # Create meter WITH graphics enabled
    meter = LightMeter('/dev/ttyACM1', graphics=True)
    
    print("\n✓ Graphics window opened")
    print("\nGraph shows:")
    print("  X-axis: Pixel position (0-3668)")
    print("  Y-axis: Normalized light intensity (0-1)")
    print("\nUpdates every 200ms")
    print("Press Ctrl+C to stop\n")
    
    try:
        measurement_count = 0
        
        while True:
            stats = meter.get_statistics()
            measurement_count += 1
            
            # Show statistics
            avg_light = stats['mean'] * 100
            print(f"[{measurement_count}] Light: {avg_light:5.1f}% | "
                  f"Range: {stats['min']*100:5.1f}%-{stats['max']*100:5.1f}% | "
                  f"Variance: ±{stats['std']*100:.1f}%")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nStopping...")
    
    finally:
        meter.close()
        print("Closed.")


if __name__ == "__main__":
    main()
