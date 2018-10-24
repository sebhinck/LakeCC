#!/usr/bin/env python

def FillLakes(fIn, fOut, sl=0.0, dz=10., zMin=None, zMax=None, rho_ice=910., rho_sea=1027., rho_fresh=1000., tind=-1, thk_if=10.):
  from netCDF4 import Dataset
  import LakeCC as LCC
  
  ncIn = Dataset(fIn, 'r')
  
  topg = getNcVarSlice(ncIn, 'topg', tind).astype("double")
  shape = topg.shape
  
  try:
    x = nc.variables['x'][:]
  except:
    x = np.arange(0, shape[1])

  try:
    y = nc.variables['y'][:]
  except:
    y = np.arange(0, shape[0])
  
  try:
    thk = getNcVarSlice(ncIn, 'thk', tind, shape).astype("double")
  except:
    print(" -> Setting it to zero")
    thk = np.zeros(shape).astype("double")

  try:
    pism_mask = getNcVarSlice(ncIn, 'pism_mask', tind, shape).astype("double")
  except:
    print (" -> Calculate it from topg, thk and sea_level.")
    try:
      sea_level = getNcVarSlice(ncIn, 'sea_level', tind, shape).astype("double")
    except:
      print (" -> Determine sea_level using SeaLevelCC model. Check if sl_mask is present.")
      try:
        sl_mask = getNcVarSlice(ncIn, 'sl_mask', tind, shape).astype("double")
      except:
        print (" -> Set sl_mask 1 at the margins.")
        sl_mask = np.zeros(shape)
        sl_mask[(0, -1),:] = 1
        sl_mask[:,(0, -1)] = 1
      #sl_mask defined
      #FIXME SL Mask not need here... 
      SLM = LCC.SeaLevelModelCC(topg, thk, rho_ice, rho_sea)
      SLM.fill2SeaLevel(sl)
      sea_level = SLM.getFloatationLevel()
      
    #Sea Level is present
    alpha = 1. - (rho_ice / rho_sea)
    pism_mask = computePismMask(topg, thk, sea_level, alpha, shape, thk_if).astype("double")
    
  #pism_mask is present
  LM = LCC.LakeModelCC(topg, thk, pism_mask, rho_ice, rho_fresh)
  LM.fillLakes(dz, zMin, zMax)
  lake_level = LM.getFloatationLevel()
          
  ncIn.close()
  
  ncOut = Dataset(fOut, 'w')
 
  xDim = ncOut.createDimension('x', len(x))
  yDim = ncOut.createDimension('y', len(y))

  x_out = ncOut.createVariable('x','f4', ['x'])
  y_out = ncOut.createVariable('y','f4', ['y'])
  
  x_out[:] = x[:]
  y_out[:] = y[:]
 
  topg_out = ncOut.createVariable('topg','f4', ['y','x'])
  topg_out[:] = topg[:,:]
  
  thk_out = ncOut.createVariable('thk','f4', ['y','x'])
  thk_out[:] = thk[:,:]
  
  pism_mask_out = ncOut.createVariable('pism_mask','f4', ['y','x'])
  pism_mask_out[:] = pism_mask[:,:]
  
  sea_level_out = ncOut.createVariable('sea_level','f4', ['y','x'])
  sea_level_out[:] = sea_level[:,:]

  sl_mask_out = ncOut.createVariable('sl_mask','f4', ['y','x'])
  sl_mask_out[:] = sl_mask[:,:]
  
  lake_level_out = ncOut.createVariable('lake_level','f4', ['y','x'])
  lake_level_out[:] = lake_level[:,:]
  
  ncOut.close()


def computePismMask(topg, thk, sea_level, alpha, shape, ice_free_thickness=10.):

  pism_mask_free_rock     = 0
  pism_mask_grounded      = 2
  pism_mask_floating      = 3
  pism_mask_free_ocean    = 4

  hgr = topg + thk
  sl = sea_level.copy()
  invalid_sl = np.isnan(sea_level)
  sl[invalid_sl] = topg[invalid_sl]
  hfl = sl + alpha * thk

  is_floating = hfl > hgr
  ice_free    = (thk < ice_free_thickness);

  mask = np.ones(shape) * pism_mask_free_rock
  mask[~ice_free & ~is_floating] = pism_mask_grounded
  mask[~ice_free & is_floating]  = pism_mask_floating
  mask[ice_free & is_floating]   = pism_mask_free_ocean

  return mask


def getNcVarSlice(nc, varname, tind = -1, shape = None):
  try:
    var = nc.variables[varname]
    dims = var.dimensions
    if len(dims) == 2:
      data = var[:,:]
    elif len(dims) == 3:
      data = var[tind, :, :]    
    else:
      raise ValueError("Wrong number of dimensions: "+str(len(dims)))
  except:
    print(varname + " not found in file.")
    raise
    
  if shape is not None:
    if shape != data.shape:
      raise ValueError("Dimensions of "+varname+ "do not match required dimensions.")
      
  return data

def main():
  options = parse_args()

  FillLakes(options.fIn, options.fOut, options.sl, options.dz, options.zMin, options.zMax, options.rhoi, options.rhos, options.rhof, options.tind, options.thk_if)

def parse_args():
  from argparse import ArgumentParser
  import os

  parser = ArgumentParser()
  parser.description = "Fill lakes"
  parser.add_argument("-i", "--input",  dest="fIn",  required=True, help="Input file", metavar="FILE", type=lambda x: is_valid_file(parser, x))
  parser.add_argument("-o", "--output", dest="fOut", help="Output file", metavar="FILE", default="out.nc", type=lambda x: os.path.abspath(x))
  parser.add_argument('-sl', "--sea-level", dest="sl", help="scalar sea-level", default=0.0, type=float)
  parser.add_argument('-dz', "--lake_level_spacing", dest="dz", help="Lake level spacing", default=10., type=float)
  parser.add_argument('-zMin', "--lake_level_min", dest="zMin", help="Lowest lake level", default=None, type=float)
  parser.add_argument('-zMax', "--lake_level_max", dest="zMax", help="Highest lake level", default=None, type=float)
  parser.add_argument('-rho_i', "--ice_density", dest="rhoi", help="Density of ice", default=910., type=float)
  parser.add_argument('-rho_s', "--sea_water_density", dest="rhos", help="Density of sea water", default=1027., type=float)
  parser.add_argument('-rho_f', "--fresh_water_density", dest="rhof", help="Density of fresh water", default=1000., type=float)
  parser.add_argument('-thk_if', "--icefree_thickness", dest="thk_if", help="Icefree thickness", default=10., type=float)
  parser.add_argument('-tind', "--time-index", dest="tind", help="index of time dimension", default=-1, type=int)
  options = parser.parse_args()
  return options

def is_valid_file(parser, arg):
  import os

  if not os.path.exists(arg):
    parser.error("The file %s does not exist!" % arg)
  else:
    return os.path.abspath(arg)  # return file path

if __name__ == "__main__":
  import numpy as np
  main()

