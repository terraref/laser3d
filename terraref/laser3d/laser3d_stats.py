from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
from rpy2.robjects import pandas2ri


class GeotiffStats(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = gdal.Open(file_path)
        self.vector = np.array(self.file.GetRasterBand(1).ReadAsArray())
        self.vector[self.vector == -9999.] = np.nan

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
    vector[vector == -9999.] = np.nan
    newvector = vector[~np.isnan(vector)]
    rstring = """
        function(angles){
          n <- length(angles)
          betapara <- RLeafAngle::computeBeta(angles)
          result <- data.frame(rbind(
            c(trait    = 'leaf_angle_twoparbeta',
              beta1    =  betapara[1],
              beta2    = betapara[2],
              mean     = betapara[1]/(betapara[1]+betapara[2]), 
              variance = betapara[1]*betapara[2]/(betapara[1]+betapara[2])/(betapara[1]+betapara[2])/(betapara[1]+betapara[2]+1), 
              n        = n)))
          return(result)
        }
        """
    rpy2.robjects.numpy2ri.activate()
    rfunc = robjects.r(rstring)
    r_df = rfunc(newvector)
    newdf = pandas2ri.ri2py(r_df)
    return newdf
