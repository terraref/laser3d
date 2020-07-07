from laser3d import GeotiffStats#, fit_rleafangle_tiff
#in order to use fit_rleafangle_tiff, you should install rpy2 so that we can call R from python

# pip install rpy2==2.8.6 for python 2

#dire should be where you put the file
dire = '/Users/mburnette/globus/heightmap_review/scanner3DTop_L2_ua-mac_2018-07-08__04-51-55-343_heightmap.tif'

#initialize the stats object
geostatsObject = GeotiffStats(dire)

#mean, without -9999. and Nan values
mean  = geostatsObject.mean_geotiff()

#variance, same constraint as mean
var = geostatsObject.var_geotiff()

#plot, save to certain directory or show
save = '/Users/mburnette/globus/heightmap_review/histogram.png'
#save the plot
geostatsObject.hist_geotiff(save)
#show the plot
geostatsObject.hist_geotiff()

failz()

######analyze the leaf angle and fit to beta distribution, still removed -9999. and nan value
fitted_result = fit_rleafangle_tiff(dire)

#beta distribution parameter one
beta1 = fitted_result['beta1']

#beta distribution parameter two
beta2 = fitted_result['beta2']

#fitted mean,variance, calculated by beta1 and beta2
fit_mean = fitted_result['mean']
fit_var = fitted_result['variance']
