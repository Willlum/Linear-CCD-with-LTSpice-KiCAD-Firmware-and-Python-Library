#!/usr/bin/python

"""
Simple Light Intensity Example

Shows how to use the LightMeter class for basic light measurements.
"""

from light_meter import LightMeter


def main():
    """Example: Measure light intensity in real-time."""
    
    # Initialize meter on the correct port
    meter = LightMeter('/dev/ttyACM1')
    
    try:
        print("\nReading light intensity...")
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
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    finally:
        meter.close()


if __name__ == "__main__":
    main()
