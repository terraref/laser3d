from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
from rpy2.robjects import pandas2ri
import laspy
from plyfile import PlyData

class GeotiffStats(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = gdal.Open(file_path)
        self.vector = np.array(self.file.GetRasterBand(1).ReadAsArray())

    def sample_geotiff(self, sample_num = 1000):
        return np.random.choice(self.vector[~np.isnan(self.vector)], sample_num)

    def mean_geotiff(self):
        return np.nanmean(self.vector)

    def var_geotiff(self):
        return np.nanvar(self.vector)

    def hist_geotiff(self):
        newv = np.concatenate(self.vector, axis=0)
        plt.hist(newv[~np.isnan(newv)], 50, normed=1, facecolor='green', alpha=0.75)
        plt.xlabel('Geotiff value')
        plt.ylabel('Probability')
        plt.title('Histogram of Geotiff')
        plt.show()


def fit_rleafangle_tiff(file_path):
    file = gdal.Open(file_path)
    vector = np.concatenate(np.array(file.GetRasterBand(1).ReadAsArray()), axis=0)
    rstring = """
        function(angles){
          n <- length(angles)
          betapara <- RLeafAngle::computeBeta(angles)
          result <- data.frame(rbind(
            c(trait    = 'leaf_angle_twoparbeta',
              mean     = betapara[1]/(betapara[1]+betapara[2]), 
              statname =  'variance',
              stat     = betapara[1]*betapara[2]/(betapara[1]+betapara[2])/(betapara[1]+betapara[2])/(betapara[1]+betapara[2]+1), 
              n        = n)))
          return(result)
        }
        """
    rpy2.robjects.numpy2ri.activate()
    rfunc = robjects.r(rstring)
    r_df = rfunc(vector)
    newdf = pandas2ri.ri2py(r_df)
    return newdf

def distinguish_leafangle_ply(plyfile):
    plydata = PlyData.read(file)
    first = True
    merged_x = plydata['vertex']['x']
    merged_y = plydata['vertex']['y']
    merged_z = plydata['vertex']['z']

    return merged_x, merged_y, merged_z


def fit_rleafangle_array(array):
    rstring = """
        function(angles){
          n <- length(angles)
          betapara <- RLeafAngle::computeBeta(angles)
          result <- data.frame(rbind(
            c(trait    = 'leaf_angle_twoparbeta',
              mean     = betapara[1]/(betapara[1]+betapara[2]), 
              statname =  'variance',
              stat     = betapara[1]*betapara[2]/(betapara[1]+betapara[2])/(betapara[1]+betapara[2])/(betapara[1]+betapara[2]+1), 
              n        = n)))
          return(result)
        }
        """
    rpy2.robjects.numpy2ri.activate()
    rfunc = robjects.r(rstring)
    r_df = rfunc(array)
    newdf = pandas2ri.ri2py(r_df)
    return newdf