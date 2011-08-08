

#####################################################################
#This software was developed by the University of Tennessee as part of the
#Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
#project funded by the US National Science Foundation. 
#See the license text in license.txt
#copyright 2008, University of Tennessee
######################################################################
"""
    Image reader. Untested. 
"""


#TODO: load and check data and orientation of the image (needs rendering)

import math, logging, os
import numpy
from DataLoader.data_info import Data2D
    
class Reader:
    """
    Example data manipulation
    """
    ## File type
    type_name = "TIF"   
    ## Wildcards
    type = ["TIF files (*.tif)|*.tif",
            "TIFF files (*.tiff)|*.tiff",
            ]
    ## Extension
    ext  = ['.tif', '.tiff']    
        
    def read(self, filename=None):
        """
        Open and read the data in a file
        
        :param file: path of the file
        """
        try:
            import Image
        except:
            msg = "tiff_reader: could not load file. Missing Image module."
            raise RuntimeError, msg
        
        # Instantiate data object
        output = Data2D()
        output.filename = os.path.basename(filename)
            
        # Read in the image
        try:
            im = Image.open(filename)
        except :
            raise  RuntimeError,"cannot open %s"%(filename)
        data = im.getdata()

        # Initiazed the output data object
        output.data = numpy.zeros([im.size[0],im.size[1]])
        output.err_data = numpy.zeros([im.size[0],im.size[1]])
        
        # Initialize 
        x_vals = []
        y_vals = [] 

        # x and y vectors
        for i_x in range(im.size[0]):
            x_vals.append(i_x)
            
        itot = 0
        for i_y in range(im.size[1]):
            y_vals.append(i_y)

        for val in data:
            try:
                value = float(val)
            except:
                logging.error("tiff_reader: had to skip a non-float point")
                continue
            
            # Get bin number
            if math.fmod(itot, im.size[0])==0:
                i_x = 0
                i_y += 1
            else:
                i_x += 1
                
            output.data[im.size[1]-1-i_y][i_x] = value
            
            itot += 1
                
        output.xbins      = im.size[0]
        output.ybins      = im.size[1]
        output.x_bins     = x_vals
        output.y_bins     = y_vals
        output.xmin       = 0
        output.xmax       = im.size[0]-1
        output.ymin       = 0
        output.ymax       = im.size[0]-1
        
        # Store loading process information
        output.meta_data['loader'] = self.type_name 
        return output
        

if __name__ == "__main__": 
    reader = Reader()
    print reader.read("../test/MP_New.sans")
    

