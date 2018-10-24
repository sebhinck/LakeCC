#!/usr/bin/env python

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
    
    if not (FilterMethod is None):
        if (FilterMethod == 'Gaussian'):
            import scipy.ndimage as ndi
            filtered = ndi.gaussian_filter(topg, sigma = FilterN,  mode = 'nearest')
            topg = filtered
            #topgFilteredV = ncout.createVariable("topg_filtered", 'f4', ['y', 'x'])
            #ncout.variables['topg_filtered'][:] = filtered

    ncout.variables['topg'][:] = topg
    
    ncout.close()
    
    
def main(argv):
  
  if len(sys.argv) > 1:
    fIn = sys.argv[1]
  else:
    fIn = 'ETOPO1_Bed_c_gmt4.nc'

  if len(sys.argv) > 2:
    fOut = sys.argv[2]
  else:
    fOut = 'out.nc'

  lim=[-180.0, 180.0, -90.0, 90.0]

  if len(sys.argv) > 3:
    lim[0] = float(sys.argv[3])
  if len(sys.argv) > 4:
    lim[1] = float(sys.argv[4])
  if len(sys.argv) > 5:
    lim[2] = float(sys.argv[5])
  if len(sys.argv) > 6:
    lim[3] = float(sys.argv[6])
    
  if len(sys.argv) > 7:
    Filter = sys.argv[7]
    if Filter == 'None':
      Filter = None
  else:
    Filter = None
    
  if len(sys.argv) > 8:
    FilterN = int(sys.argv[8])
  else:
    FilterN = 1

  CropAndFilterMap(fIn, fOut, lim, FilterN, Filter)


if __name__ == "__main__":
  import sys
  main(sys.argv)
  
