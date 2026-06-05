#!/usr/bin/python

"""
Data model classes for TCD1304 CCD measurements.

Handles frame data loading, parsing, and storage for spectrographic data.
"""

import glob
import operator
import numpy as np

from utils import generate_x_vector


class LccdFrame:
    """
    Represents a single CCD measurement frame from a data file.
    
    Attributes:
        parent: Reference to parent LccdData object
        data: numpy array of pixel values
        offset: Time offset in seconds
        Various measurement parameters (shutter, interval, clock, etc.)
    """

    def __init__(self, content, parent, offsetdigits=6, dtype=None):
        """
        Initialize a frame by parsing content lines from a data file.
        
        Args:
            content: List of text lines from data file
            parent: Parent LccdData object
            offsetdigits: Decimal places to round offset to
            dtype: Unused, for compatibility
        """
        self.parent = parent
        self.accumulate = 0

        while len(content):
            line = content[0].lower().strip()
            if not len(line):
                content = content[1:]
                continue

            # Parse ASCII data section
            if line.startswith('# data ascii'):
                self.datalen = int(line.split()[3])
                data = []
                n = 1
                for l in content[1:]:
                    n += 1
                    if l.lower().startswith('# end data'):
                        break
                    data.append(float(l))
                self.data = np.array(data)
                content = content[n:]

            # Parse header lines (start with #)
            elif line[0] == '#':
                line = line[1:].strip()

                if '=' in line:
                    # Execute assignment statements to populate attributes
                    exec(line, self.__dict__)
                elif line.lower().startswith('timestamp'):
                    key, value = line.split(maxsplit=1)
                elif key == 'adcdata':
                    self.__dict__[key] = [a for a in map(float, value.split())]

                content = content[1:]
            else:
                print('Warning: empty line in frame')
                content = content[1:]

        # Copy measurement parameters to parent if not already set
        for key in ['INTERVAL', 'CLOCK', 'MODE', 'SETS', 'ACCUMULATE', 'OUTERCOUNTER',
                    'interval', 'clock', 'mode', 'sets', 'accumulate', 'outercounter']:
            if key in self.__dict__ and key not in parent.__dict__:
                parent.__dict__[key] = self.__dict__[key]

        # Normalize elapsed time to offset
        if 'ELAPSED' in self.__dict__:
            self.__dict__['offset'] = self.ELAPSED / 1.0e6
        elif 'elapsed' in self.__dict__:
            self.__dict__['offset'] = self.elapsed / 1.0e6
        elif 'TRIGGERELAPSED' in self.__dict__:
            self.__dict__['ELAPSED'] = self.TRIGGERELAPSED
            self.__dict__['offset'] = self.TRIGGERELAPSED / 1.0e6
        elif 'tiggerelapsed' in self.__dict__:
            self.__dict__['triggerelapsed'] = self.triggerelapsed
            self.__dict__['offset'] = self.triggerelapsed / 1.0e6

        if 'offset' in self.__dict__ and offsetdigits:
            self.offset = round(self.offset, offsetdigits)

    def __len__(self):
        """Return the number of data points in this frame."""
        return len(self.data) if hasattr(self, 'data') else 0

    def get(self, expression):
        """
        Retrieve an attribute or evaluate an expression.
        
        Args:
            expression: Attribute name or Python expression
        
        Returns:
            Value of attribute or result of expression
        """
        if expression in self.__dict__:
            return self.__dict__[expression]
        else:
            exec('retv=' + expression, self.__dict__)
            return self.__dict__.get('retv')

    def dump(self):
        """Print all attributes for debugging."""
        for key, val in self.__dict__.items():
            if key == 'parent' and val is not None:
                print(key, self.parent.filename)
            elif key != '__builtins__':
                print(key, val)


class LccdData:
    """
    Container for all CCD measurement frames from a single data file.
    
    Handles loading, parsing, and organizing frame data along with
    calibration coefficients and measurement parameters.
    
    Attributes:
        filename: Path to data file
        frames: List of LccdFrame objects
        coefficients: Wavelength calibration polynomial coefficients
        xdata: X-axis data (pixels or wavelengths)
        wavelengths: Wavelength values for each pixel
    """

    def __init__(self, filename, dtype=None, relatedobject=None, 
                 offsetdigits=6, verbose=False):
        """
        Load and parse a CCD data file.
        
        Args:
            filename: Path to .lccd data file
            dtype: Unused, for compatibility
            relatedobject: Related object for cross-reference
            offsetdigits: Decimal places for time offset rounding
            verbose: Enable verbose output
        
        Raises:
            ValueError: If file format is invalid
        """
        self.filename = filename
        self.relatedobject = relatedobject

        with open(filename, 'r') as f:
            content = f.read().splitlines()

        if not content[0].startswith("# LCCD"):
            print(content[0])
            raise ValueError("file is not LCCD format")

        # Parse header
        self.version = content[0]
        self.filedate = content[1]
        self.chiptemperature = None
        self.coefficients = None

        for n, line in enumerate(content[2:], start=2):
            if line[0] != '#':
                raise ValueError('lines in file header need to start with #')

            line = line[1:].strip()

            if line.lower().startswith("header end"):
                content = content[n + 1:]
                break

            # Support version 0 file format
            if line.startswith("shutter"):
                content = content[n:]
                break

            # Parse key=value assignments
            if '=' in line:
                exec(line, self.__dict__)
            else:
                # Parse key: value format
                if ':' in line:
                    key, value = line.split(':', maxsplit=1)
                else:
                    key, value = line.split(maxsplit=1)

                if key == 'coefficients':
                    self.coefficients = [a for a in map(float, value.split())]
                else:
                    # Try to parse as int, then float, then string
                    try:
                        self.__dict__[key] = int(value)
                    except ValueError:
                        try:
                            self.__dict__[key] = float(value)
                        except ValueError:
                            self.__dict__[key] = str(value)

        # Post-header setup
        if 'datalength' in self.__dict__:
            self.xdata = generate_x_vector(self.datalength, self.coefficients)
            self.wavelengths = self.xdata
            self.pixels = np.linspace(0, self.datalength, self.datalength)

        # Load frames
        self.frames = []

        while len(content):
            # Skip blank lines
            for n, line in enumerate(content):
                if line.strip():
                    break
            content = content[n:]
            if not len(content):
                break

            # Find next blank lines
            for m, line in enumerate(content):
                if not line.strip():
                    break
            if not len(content[:m]):
                break

            frame = LccdFrame(content[:m], self, offsetdigits)
            if len(frame):
                self.frames.append(frame)
            else:
                raise ValueError('empty frame')

            content = content[m:]

        # Adjust offsets for pulse lead-in
        if 'pulse_leadin' in self.__dict__:
            offset = self.frames[self.pulse_leadin].offset
            for f in self.frames:
                f.offset -= offset
                if offsetdigits:
                    f.offset = round(f.offset, offsetdigits)

    def __len__(self):
        """Return the number of frames."""
        return len(self.frames)

    def get(self, expression):
        """
        Retrieve an attribute or evaluate an expression.
        
        Args:
            expression: Attribute name or Python expression
        
        Returns:
            Value of attribute or result of expression
        """
        if expression in self.__dict__:
            return self.__dict__[expression]
        else:
            exec('retv=' + expression, self.__dict__)
            return self.__dict__.get('retv')

    def getlist(self, attr_name):
        """
        Get a list of attribute values across all frames.
        
        Args:
            attr_name: Name of attribute to extract
        
        Returns:
            List (or numpy array if possible) of values
        """
        rets = []
        for f in self.frames:
            rets.append(f.get(attr_name))

        try:
            rets = np.array(rets)
        except Exception:
            pass

        return rets

    def dump(self):
        """Print all attributes and frame data for debugging."""
        print("***************************")
        for key, val in self.__dict__.items():
            if key == 'relatedobject' and val is not None:
                if 'filename' in self.relatedobject.__dict__:
                    print(key, self.relatedobject.filename)
            elif key not in ['__builtins__', 'frames']:
                print(key, val)

        for n, frame in enumerate(self.frames):
            print("---------------------------")
            print("*frame", n)
            frame.dump()

        if self.relatedobject is not None:
            try:
                self.relatedobject.dump()
            except Exception as e:
                print(e)


class LccdDataset:
    """
    Collection of LccdData objects from multiple files.
    
    Supports loading multiple data files, sorting, and accessing
    data across the entire dataset.
    
    Attributes:
        dataset: List of LccdData objects
    """

    def __init__(self, filespecs=None, dataset=None, sort_attr=None, verbose=False):
        """
        Initialize a dataset from files or LccdData objects.
        
        Args:
            filespecs: File path or glob pattern(s) to load
            dataset: List of LccdData objects to use instead of files
            sort_attr: Attribute name to sort by
            verbose: Enable verbose output
        """
        self.dataset = []

        if filespecs is not None:
            if not isinstance(filespecs, list):
                filespecs = [filespecs]

            for filespec in filespecs:
                for filespec_ in glob.glob(filespec):
                    if filespec_.endswith('lccd'):
                        lccd = LccdData(filespec_, verbose=verbose)
                        self.dataset.append(lccd)

        if dataset is not None:
            for d in dataset:
                if isinstance(d, LccdData):
                    self.dataset.append(d)
                else:
                    raise ValueError('not LccdData instance')

        if sort_attr is not None:
            self.sort(sort_attr)

    def get(self, expression):
        """
        Retrieve an attribute or evaluate an expression.
        
        Args:
            expression: Attribute name or Python expression
        
        Returns:
            Value of attribute or result of expression
        """
        if expression in self.__dict__:
            return self.__dict__[expression]
        else:
            exec('retv=' + expression, self.__dict__)
            return self.__dict__.get('retv')

    def getlist(self, attr_name):
        """
        Get a list of attribute values across all data objects.
        
        Args:
            attr_name: Name of attribute to extract
        
        Returns:
            List (or numpy array if possible) of values
        """
        rets = []
        for d in self.dataset:
            rets.append(d.get(attr_name))

        try:
            rets = np.array(rets)
        except Exception:
            pass

        return rets

    def sort(self, attr_name):
        """Sort dataset by the specified attribute."""
        print('sort', attr_name)
        self.dataset.sort(key=operator.attrgetter(attr_name))

    def slices(self, n, currentnorm=False):
        """
        Extract the nth frame from all data objects as slices.
        
        Args:
            n: Frame index
            currentnorm: If True, normalize by related object's avgcurrent
        
        Returns:
            numpy array of shape (num_datasets, frame_length)
        """
        slices_ = []
        for d in self.dataset:
            if currentnorm:
                slices_.append(d.frames[n].data / d.relatedobject.avgcurrent)
            else:
                slices_.append(d.frames[n].data)

        return np.array(slices_)

    def __len__(self):
        """Return the number of data objects."""
        return len(self.dataset)
