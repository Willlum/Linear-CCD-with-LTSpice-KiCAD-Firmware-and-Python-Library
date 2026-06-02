#!/usr/bin/python

"""
Simple Light Intensity Example with Graphics

Shows how to use the LightMeter class with real-time graphical display.
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

from light_meter import LightMeter


def main():
    """Example: Measure light intensity with real-time graph."""
    
    # Initialize meter WITH graphics window
    meter = LightMeter('/dev/ttyACM1', graphics=True)
    
    try:
        print("\nMonitoring light intensity with graphics...")
        print("Press Ctrl+C to stop\n")
        
        import time
        measurement_count = 0
        
        while True:
            # Get light statistics
            stats = meter.get_statistics()
            measurement_count += 1
            
            # Display results
            print(f"Measurement #{measurement_count}")
            print(f"  Light Level: {stats['mean']*100:.1f}%")
            print(f"  Range: {stats['min']*100:.1f}% - {stats['max']*100:.1f}%")
            print(f"  Variation: ±{stats['std']*100:.1f}%")
            print()
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    finally:
        meter.close()


if __name__ == "__main__":
    main()
