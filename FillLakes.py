#!/usr/bin/env python

from __future__ import absolute_import, division, print_function

#####################################################################
## Usage of this script #############################################
#####################################################################
#
#Fill lakes
#
#optional arguments:
#  -h, --help            show this help message and exit
#  -i FILE, --input FILE
#                        Input file
#  -o FILE, --output FILE
#                        Output file
#  -sl SL, --sea-level SL
#                        scalar sea-level
#  -dz DZ, --lake_level_spacing DZ
#                        Lake level spacing
#  -zMin ZMIN, --lake_level_min ZMIN
#                        Lowest lake level
#  -zMax ZMAX, --lake_level_max ZMAX
#                        Highest lake level
#  -rho_i RHOI, --ice_density RHOI
#                        Density of ice
#  -rho_s RHOS, --sea_water_density RHOS
#                        Density of sea water
#  -rho_f RHOF, --fresh_water_density RHOF
#                        Density of fresh water
#  -thk_if THK_IF, --icefree_thickness THK_IF
#                        Icefree thickness
#  -tind TIND, --time-index TIND
#                        index of time dimension
#  -ms, --setMarginSink  set margin of domain as sink
#  -nms, --not-setMarginSink
#                        not set margin of domain as sink
#####################################################################



def FillLakes(fIn, fOut, sl=0.0, dz=10., zMin=None, zMax=None, rho_ice=910., rho_sea=1027., rho_fresh=1000., tind=-1, thk_if=10., setMarginSink=True):
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
        sl_mask = np.zeros(shape).astype("double")
        sl_mask[(0, -1),:] = 1
        sl_mask[:,(0, -1)] = 1
      #sl_mask defined
      t_sl = myTimer('Sea level calculation')
      SLM = LCC.SeaLevelModelCC(topg, thk, sl_mask, rho_ice, rho_sea)
      SLM.fill2SeaLevel(sl)
      sea_level = SLM.getFloatationLevel()
      t_sl.toc()

    #Sea Level is present
    alpha = 1. - (rho_ice / rho_sea)
    pism_mask = computePismMask(topg, thk, sea_level, alpha, shape, thk_if).astype("double")
    
  #pism_mask is present
  t_ll = myTimer('Lake level caluculation')
  LM = LCC.LakeModelCC(topg, thk, pism_mask, rho_ice, rho_fresh, setMarginSink)
  LM.fillLakes(dz, zMin, zMax)
  lake_level = LM.getFloatationLevel()
  t_ll.toc()


  zMin_tmp = zMin
  if zMin_tmp is None:
    zMin_tmp = np.min(topg)  
  zMax_tmp = zMax
  if zMax_tmp is None:
    zMax_tmp = np.max(topg)
  print("Size of map: "+str(shape[0])+"x"+str(shape[1])+", number of levels checked: "+str(int( (zMax_tmp - zMin_tmp)/dz )))
          
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

  FillLakes(options.fIn, options.fOut, options.sl, options.dz, options.zMin, options.zMax, options.rhoi, options.rhos, options.rhof, options.tind, options.thk_if, options.ms)

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
  parser.add_argument('-ms','--setMarginSink', dest='ms', action='store_true', help="set margin of domain as sink")
  parser.add_argument('-nms','--not-setMarginSink', dest='ms', action='store_false', help="not set margin of domain as sink")
  parser.set_defaults(ms=True)

  options = parser.parse_args()
  return options

def is_valid_file(parser, arg):
  import os

  if not os.path.exists(arg):
    parser.error("The file %s does not exist!" % arg)
  else:
    return os.path.abspath(arg)  # return file path



import os, time
from datetime import timedelta

try:
    time.monotonic
except:
    time.monotonic = time.time

class myTimer():
    def __init__(self, Name = None, start=True):
        self.Name = Name
        self.running = False
        if start:
            self.tic()
            
    def tic(self):
        #if self.Name is not None:
        #    print(self.Name ,"started at:", time.strftime('%X', time.localtime()))
            
        self.running = True            
        self.StartTime = time.monotonic()
        
    def toc(self):
        if self.running:
            self.EndTime = time.monotonic()
            self.running = False
            dt = timedelta(seconds = self.EndTime - self.StartTime)
            #if self.Name is not None:
            #    print(self.Name ,"ended at:", time.strftime('%X', time.localtime()))
        else:
            dt = None
            
        self.reportEnd(dt)
        
    def report(self, dt, verb='running for'):
        if self.Name is not None:
            print(self.Name ,verb, dt)
        else:
            print(dt)
            
    def reportEnd(self, dt):
        self.report(dt, 'took')
        
    def elapsed(self):
        now = time.monotonic()
        dt = timedelta(seconds = now - self.StartTime)
        self.report(dt)



if __name__ == "__main__":
  import numpy as np
  main()

