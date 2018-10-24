# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 14:31:27 2017

@author: sebastian
"""

def getIndFromCoord(x, x_coord):
    
    return abs(x_coord - x).argmin()


def getIndRangeFromCoord(xmin, xmax, ymin, ymax, x, y):
    
    xminInd = getIndFromCoord(xmin, x)
    xmaxInd = getIndFromCoord(xmax, x)
    yminInd = getIndFromCoord(ymin, y)
    ymaxInd = getIndFromCoord(ymax, y)
    
    return [xminInd, xmaxInd, yminInd, ymaxInd]


def CropAndFilterMap(fIn, fOut, lim, FilterN = 10, FilterMethod = 'square'):
    
    import netCDF4 as NC
    import numpy as np
    
    ncIn = NC.Dataset(fIn)
    
    xD = ncIn.dimensions['x']
    yD = ncIn.dimensions['y']
    
    xV = ncIn.variables['x']
    yV = ncIn.variables['y']
    topgV = ncIn.variables['z']
    
    xmin, xmax, ymin, ymax = getIndRangeFromCoord(lim[0], lim[1], lim[2], lim[3], xV[:], yV[:])
    xind = range(xmin, xmax + 1)
    yind = range(ymin, ymax + 1)    
    
    
    topg = np.copy(topgV[yind, xind]).astype("double")
   
    ncout = NC.Dataset(fOut, 'w')
    
    xDim = ncout.createDimension('x', len(xind))
    yDim = ncout.createDimension('y', len(yind))

    xN = ncout.createVariable('x','f4' , 'x')
    ncout.variables['x'][:] = xV[xind]
    
    yN = ncout.createVariable('y', 'f4', 'y')
    ncout.variables['y'][:] = yV[yind]
    
    topgN = ncout.createVariable('topg' , 'f4', ['y', 'x'])
    ncout.variables['topg'][:] = topg
    
    if not (FilterMethod is None):
        if (FilterMethod == 'Gaussian'):
            import scipy.ndimage as ndi
            filtered = ndi.gaussian_filter(topg, sigma = FilterN,  mode = 'nearest')
            
            topgFilteredV = ncout.createVariable("topg_filtered", 'f4', ['y', 'x'])
            ncout.variables['topg_filtered'][:] = filtered
    
    ncout.close()
