#!/usr/bin/python

"""
Light Intensity Meter - Simplified CCD Controller for Light Measurement

A simplified interface to the TCD1304 controller for measuring normalized
light intensity without spectrographic functionality.

Usage:
    from light_meter import LightMeter
    
    meter = LightMeter('/dev/ttyACM1')
    intensity = meter.get_light_intensity()
    print(f"Light intensity: {intensity:.4f} (0-1 scale)")
    meter.close()
"""

import numpy as np
from TCD1304Rev2Controller import LccdController


class LightMeter:
    """
    Simplified light intensity measurement interface.
    
    Provides normalized light intensity (0-1) without spectrographic features.
    """
    
    def __init__(self, port, debug=False):
        """
        Initialize the light meter.
        
        Args:
            port: Serial port (e.g., '/dev/ttyACM1')
            debug: Enable debug output
        """
        # Initialize controller WITHOUT graphics/GUI (simpler, faster)
        self.controller = LccdController(
            port,
            monitor=False,      # No text window
            graphics=False,     # No graphics window
            gui=False,          # No GUI
            debug=debug
        )
        
        print(f"Light meter initialized on {port}")
        print(f"Sensor: {self.controller.sensor}")
        print(f"Pixels: {self.controller.datalength}")
        print(f"Dark pixels: {self.controller.darklength}")
        print(f"Voltage range: {self.controller.vfs}V")
    
    def get_light_intensity(self):
        """
        Get normalized light intensity (0-1 scale).
        
        Returns:
            float: Normalized light intensity (0.0 = dark, 1.0 = full brightness)
        """
        # Wait for data to be available
        self.controller.wait(timeout=5)
        
        # Get data from queue
        while not self.controller.dataqueue.empty():
            record = self.controller.dataqueue.get()
            
            # Unpack record (same structure as saved data)
            if isinstance(record, list) and len(record) > 0:
                ycols = record[0]  # First element is the data
                
                if ycols and len(ycols) > 0:
                    data = ycols[0]  # First y column
                    
                    # Normalize to 0-1 range
                    # Data is already in voltage (vperbit applied by reader)
                    normalized = data / self.controller.vfs
                    
                    return float(np.mean(normalized))
        
        return 0.0
    
    def get_pixel_data(self):
        """
        Get raw pixel data (already in voltage, 0 to vfs).
        
        Returns:
            numpy array: Voltage values for each pixel
        """
        self.controller.wait(timeout=5)
        
        while not self.controller.dataqueue.empty():
            record = self.controller.dataqueue.get()
            
            if isinstance(record, list) and len(record) > 0:
                ycols = record[0]
                if ycols and len(ycols) > 0:
                    return ycols[0]
        
        return np.zeros(self.controller.datalength)
    
    def get_normalized_pixels(self):
        """
        Get normalized pixel data (0-1 scale).
        
        Returns:
            numpy array: Normalized intensity for each pixel (0.0 to 1.0)
        """
        data = self.get_pixel_data()
        return data / self.controller.vfs
    
    def get_statistics(self):
        """
        Get light intensity statistics.
        
        Returns:
            dict: {
                'mean': Average normalized intensity,
                'min': Minimum pixel value,
                'max': Maximum pixel value,
                'std': Standard deviation,
                'sum': Total light (sum of all pixels)
            }
        """
        normalized = self.get_normalized_pixels()
        
        return {
            'mean': float(np.mean(normalized)),
            'min': float(np.min(normalized)),
            'max': float(np.max(normalized)),
            'std': float(np.std(normalized)),
            'sum': float(np.sum(normalized))
        }
    
    def close(self):
        """Close the meter and release resources."""
        self.controller.close()
        print("Light meter closed")


# ============================================================================
# Example usage
# ============================================================================

if __name__ == "__main__":
    import time
    
    # Initialize meter
    meter = LightMeter('/dev/ttyACM1', debug=False)
    
    try:
        print("\n" + "="*60)
        print("Light Intensity Measurements")
        print("="*60)
        
        # Take 5 measurements
        for i in range(5):
            print(f"\nMeasurement {i+1}:")
            
            # Get statistics
            stats = meter.get_statistics()
            
            print(f"  Average intensity: {stats['mean']:.4f} (0-1 scale)")
            print(f"  Min: {stats['min']:.4f}, Max: {stats['max']:.4f}")
            print(f"  Std Dev: {stats['std']:.4f}")
            print(f"  Total light: {stats['sum']:.1f}")
            
            time.sleep(1)  # Wait 1 second between measurements
        
        print("\n" + "="*60)
        
    finally:
        meter.close()
