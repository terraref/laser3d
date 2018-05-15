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


def fit_leafangle_r(file_path):
    file = gdal.Open(file_path)
    vector = np.concatenate(np.array(file.GetRasterBand(1).ReadAsArray()), axis=0)
    rstring = """
        function(angles){
          x <- LeafAngle::fitdistribution(angles, 'ellipsoid')
          n <- length(angles)
    
          allfits <- LeafAngle::fitalldistributions(angles)$allfits
    
          result <- data.frame(rbind(
            c(trait    = 'leaf_angle_twoparbeta',
              mean     = allfits$twoparbeta$distpars[1], 
              statname =  'variance',
              stat     = allfits$twoparbeta$distpars[2], 
              n        = n),
            c(trait    = 'chi_leaf',
              mean     = allfits$ellipsoid$distpars, 
              statname =  'loglik',
              stat     = allfits$twoparbeta$loglik, 
              n        = n)))
          return(result)
        }
    """

    # utils.install_packages('LeafAngle')
    rpy2.robjects.numpy2ri.activate()
    rfunc = robjects.r(rstring)
    r_df = rfunc(vector)
    newdf = pandas2ri.ri2py(r_df)
    return newdf
