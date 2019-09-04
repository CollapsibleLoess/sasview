"""
Python implementation of C extension bsl_loader.c
"""
import sys
import struct

import numpy as np

class Loader():

    def __init__(self, filename, frames, pixels, rasters, swap_bytes):
        self.filename = filename
        self.n_frames = frames
        self.n_pixels = pixels
        self.n_rasters = rasters
        self.swap_bytes = swap_bytes
        #Placeholder value
        self.frame = 0

    #File to load.
    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        _filename = self.try_convert(str, filename)
        self._filename = _filename

    #Number of frames in the file.
    @property
    def n_frames(self):
        return self._n_frames

    @n_frames.setter
    def n_frames(self, n_frames):
        _n_frames = self.try_convert(int, n_frames)
        self._n_frames = _n_frames

    #Frame to load.
    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, frame):
        _frame = self.try_convert(int, frame)
        self._frame = _frame

    #Number of pixels in the file.
    @property
    def n_pixels(self):
        return self._n_pixels

    @n_pixels.setter
    def n_pixels(self, n_pixels):
        _n_pixels = self.try_convert(int, n_pixels)
        self._n_pixels = _n_pixels

    #Number of rasters in the file (int)
    @property
    def n_rasters(self):
        return self._n_rasters

    @n_rasters.setter
    def n_rasters(self, n_rasters):
        _n_rasters = self.try_convert(int, n_rasters)
        self._n_rasters = _n_rasters

    #Whether or not the bytes are in reverse order (int)
    @property
    def swap_bytes(self):
        return self._swap_bytes

    @swap_bytes.setter
    def swap_bytes(self, swap_bytes):
        _swap_bytes = self.try_convert(bool, swap_bytes)
        self._swap_bytes = _swap_bytes


    def try_convert(self, type, value):
        """
        Attempts to cast value as a type type.
        :return: value cast to type, type(value) or None if not possible.
        """
        return_val = None
        try:
            return_val = type(value)
        except:
            return_val = None

        return return_val

    def __str__(self):
        """
        Print the objects params.
        """
        desc = "Filename: " + self.filename + "\n"
        desc += "n_frames: " + str(self.n_frames) + "\n"
        desc += "frame: " + str(self.frame) + "\n"
        desc += "n_pixels: " + str(self.n_pixels) + "\n"
        desc += "n_rasters: " + str(self.n_rasters) + "\n"
        desc += "swap_bytes: " + str(self.swap_bytes) + "\n"
        return desc

    #May be irrelevant if np.fromfile is used instead of base
    #python open/read/etc.
    def reverse_float(self, in_float):
        """
        Reverses the order of the bytes of a float.
        :param: in_float, float to be reversed.
        :return: float value reversed.

        """
        in_float = self.try_convert(np.float64, in_float)
        bits = in_float.byteswap()
        return bits

    def load_data(self):
        """
        Load the data into a numpy array.
        """
        #return self.numpy_load_data()

        data = np.zeros([self.n_rasters, self.n_pixels], dtype=np.float64)

        float_size = 4

        try:
            input_file = open(self.filename, 'rb')
        except:
            raise RuntimeError("Unable to open file: ", self.filename)

        offset = self.n_pixels * self.n_rasters * self.frame * float_size
        input_file.seek(offset)

        for raster in range(self.n_rasters):
            for pixel in range(self.n_pixels):
                val = 0
                try:
                    #Attempt to read 4 bytes into val
                    val = input_file.read(float_size)
                except:
                    raise RuntimeError("Error reading file or EOF reached")

                #Convert the 4 bytes to type 'float'
                val_float = struct.unpack('f', val)[0]

                if self.swap_bytes == 0:
                    val_float = self.reverse_float(val_float)

                data[raster, pixel] = val_float

        return data

    def numpy_load_data(self):
        #Only accurate to about 6/7 decimal places even though should be reading same
        #number of bytes as the default method.

        data = np.zeros([self.n_rasters, self.n_pixels], dtype=np.float32)

        #Should be 4 byte float, big or little endian depending on swap_bytes
        dtype = ('>f4', '<f4')[self.swap_bytes]

        float_size = 4

        offset = self.n_pixels * self.n_rasters * self.frame * float_size

        load = np.fromfile(self.filename, dtype='f4')
        #with numpy 1.17, np.fromfile(self.filename, dtype=dtype, offset=offset)

        return load
