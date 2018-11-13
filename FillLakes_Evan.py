#!/usr/bin/env python

from __future__ import absolute_import, division, print_function


def FillLakes(year, topo_file, topo_filtered_file, inDir=".", fOut="./out.nc", sl=0.0, dz=10., zMin=None, zMax=None, rho_ice=910., rho_sea=1027., rho_fresh=1000., thk_if=10., setMarginSink=True):
  from netCDF4 import Dataset
  import LakeCC as LCC

  fdeform = os.path.abspath( os.path.join(inDir, "deform", str(year)+".nc") )
  fthk = os.path.abspath( os.path.join(inDir, "thickness", str(year)+".nc") )
  fusurf = os.path.abspath( os.path.join(inDir, "topo", str(year)+".nc") )
  
  ncDeform = Dataset(fdeform, 'r')
  ncThk   = Dataset(fthk, 'r')
  ncTopo= Dataset(topo_file, 'r')

  if (topo_file is not None):
    ncTopo = Dataset(topo_file, 'r')
    topg = getNcVarSlice(ncTopo, ['z', 'bedrock_topography'])
  else:
    ncTopo = Dataset(fusurf, 'r')
    topg = getNcVarSlice(ncTopo, 'z')
    topg[np.isnan(topg)] = -4300.     #This is a fill value that fits good to that edge that is missing in the topography dataset of North America!

  shape = topg.shape

  if (topo_filtered_file is not None):
    ncTopoFiltered = Dataset(topo_filtered_file, 'r')
    topg_filtered = getNcVarSlice(ncTopoFiltered, ['z', 'bedrock_topography'], shape)
    ncTopoFiltered.close()
  else:
    ncTopoFiltered = None

  dx = 1.0
  try:
    x = ncTopo.variables['x'][:]
    dx = (x[1] -x[0])/1000.     #dx in km, not m
  except:
    x = np.arange(0, shape[1])

  try:
    y = ncTopo.variables['y'][:]
  except:
    y = np.arange(0, shape[0])

  try:
    mapping = ncTopo.variables['mapping']
  except:
    mapping = None

  try:
    lat = ncTopo.variables['lat']
  except:
    lat = None

  try:
    lon = ncTopo.variables['lon']
  except:
    lon = None

  if (lat is None or lon is None):
    lat = None
    lon = None

  try:
    proj4 = ncTopo.getncattrs('proj4')
  except:
    proj4 = None

  try:
    thk = getNcVarSlice(ncThk, 'z', shape)
    thk[thk < 0] = 0.0
  except:
    print("   -> Setting it to zero")
    thk = np.zeros(shape)

  ncThk.close()

  if (topo_file is None):
    #Loaded Usurf, need to subtract ice thickness
    topg = topg - thk

  try:
    deform = getNcVarSlice(ncDeform, 'z', shape)
  except:
    print("   -> Setting it to zero")
    deform = np.zeros(shape)

  ncDeform.close()
  
  deform[np.isnan(deform)] = 0.0

  if (topo_file is not None):
    topg = topg - deform
  
  if ncTopoFiltered is not None:
    topg_filtered = topg_filtered - deform
  else:
    topg_filtered = topg

  print ("   -> Set sl_mask 1 at the margins.")
  sl_mask = np.zeros(shape)
  sl_mask[(0, -1),:] = 1
  sl_mask[:,(0, -1)] = 1

  t_sl = myTimer('Sea level calculation')
  sea_level = LCC.SeaLevelModelCC(topg_filtered, thk, sl_mask, rho_ice, rho_sea, thk_if, sl)
  t_sl.toc()

  #Sea Level is present
  alpha = 1. - (rho_ice / rho_sea)
  ocean_mask = computeOceanMask(topg, thk, sea_level, alpha, shape)
  
  #ocean_mask is present
  t_ll = myTimer('Lake level caluculation')
  lake_level_filtered = LCC.LakeModelCC(topg_filtered, thk, ocean_mask, rho_ice, rho_fresh, thk_if, setMarginSink, dz, zMin, zMax)
  t_ll.toc()

  zMin_tmp = zMin
  if zMin_tmp is None:
    zMin_tmp = np.min(topg)

  zMax_tmp = zMax
  if zMax_tmp is None:
    zMax_tmp = np.max(topg)

  print("Size of map: "+str(shape[0])+"x"+str(shape[1])+", number of levels checked: "+str(int( (zMax_tmp - zMin_tmp)/dz )))
  print("")
  
  lake_level = lake_level_filtered.copy()
  alpha_fresh = 1. - (rho_ice / rho_fresh)
  lake_mask = computeOceanMask(topg, thk, lake_level, alpha_fresh, shape)
  lake_level[lake_mask < 1] = np.nan

  lake_depth = lake_level - topg
  lake_depth_filtered = lake_level_filtered - topg

  ncOut = Dataset(fOut, 'w')

  if proj4 is not None:
    ncOut.proj4 = proj4

  if mapping is not None:
    mapping_out = ncOut.createVariable(mapping.name, mapping.datatype, mapping.dimensions)
    mapping_out[:] = mapping[:]
    mapping_out.setncatts(mapping.__dict__)

  missing_value = -2.e+09

  xDim = ncOut.createDimension('x', len(x))
  yDim = ncOut.createDimension('y', len(y))
  tDim = ncOut.createDimension('t', 1)

  x_out = ncOut.createVariable('x','f4', ['x'])
  x_out.units = "m"
  x_out.axis = "X"
  y_out = ncOut.createVariable('y','f4', ['y'])
  y_out.units = "m"
  y_out.axis = "Y"
  t_out = ncOut.createVariable('time','f4', ['t'])
  t_out.units = "years"
  t_out.axis = "T"

  x_out[:] = x[:]
  y_out[:] = y[:]
  t_out[:] = year

  if lon is not None:
    lon_out = ncOut.createVariable(lon.name, lon.datatype, lon.dimensions)
    lon_out[:] = lon[:]
    lon_out.setncatts(lon.__dict__)
    lon_out.delncattr('bounds')

    lat_out = ncOut.createVariable(lat.name, lat.datatype, lat.dimensions)
    lat_out[:] = lat[:]
    lat_out.setncatts(lat.__dict__)
    lat_out.delncattr('bounds')

  topg_out = ncOut.createVariable('topg','f4', ['t','y','x'])
  topg_out[:] = topg[:,:]
  topg_out.units = "m"
  if mapping is not None:
    topg_out.grid_mapping = mapping.name
  if lon is not None:
    topg_out.coordinates = "lat lon"
  
  #topg_filtered_out = ncOut.createVariable('topg_filtered','f4', ['t','y','x'])
  #topg_filtered_out[:] = topg_filtered[:,:]
  #topg_filtered_out.units = "m"

  thk_out = ncOut.createVariable('thk','f4', ['t','y','x'])
  thk_out[:] = thk[:,:]
  thk_out.units = "m"
  if mapping is not None:
    thk_out.grid_mapping = mapping.name
  if lon is not None:
    thk_out.coordinates = "lat lon"

  ocean_mask_out = ncOut.createVariable('ocean_mask','i', ['t','y','x'])
  ocean_mask_out[:] = ocean_mask[:,:]
  if mapping is not None:
    ocean_mask_out.grid_mapping = mapping.name
  if lon is not None:
    ocean_mask_out.coordinates = "lat lon"

  sea_level_out = ncOut.createVariable('sea_level','f4', ['t','y','x'], fill_value=missing_value)
  sea_level_tmp = sea_level.copy()
  sea_level_tmp[np.isnan(sea_level)] = missing_value
  sea_level_out[:] = sea_level_tmp[:,:]
  sea_level_out.units = "m"
  if mapping is not None:
    sea_level_out.grid_mapping = mapping.name
  if lon is not None:
    sea_level_out.coordinates = "lat lon"

  #sl_mask_out = ncOut.createVariable('sl_mask','i', ['t','y','x'])
  #sl_mask_out[:] = sl_mask[:,:]

  lake_level_out = ncOut.createVariable('lake_level','f4', ['t','y','x'], fill_value=missing_value)
  lake_level_tmp = lake_level.copy()
  lake_level_tmp[np.isnan(lake_level)] = missing_value
  lake_level_out[:] = lake_level_tmp[:,:]
  lake_level_out.units = "m"
  if mapping is not None:
    lake_level_out.grid_mapping = mapping.name
  if lon is not None:
    lake_level_out.coordinates = "lat lon"
  
  #lake_level_filtered_out = ncOut.createVariable('lake_level_filtered','f4', ['t','y','x'], fill_value=missing_value)
  #lake_level_filtered_tmp = lake_level_filtered.copy()
  #lake_level_filtered_tmp[np.isnan(lake_level_filtered)] = missing_value
  #lake_level_filtered_out[:] = lake_level_filtered_tmp[:,:]
  #lake_level_filtered_out.units = "m"

  lake_depth_out = ncOut.createVariable('lake_depth','f4', ['t','y','x'], fill_value=missing_value)
  lake_depth_tmp = lake_depth.copy()
  lake_depth_tmp[np.isnan(lake_depth)] = missing_value
  lake_depth_out[:] = lake_depth_tmp[:,:]
  lake_depth_out.units = "m"
  if mapping is not None:
    lake_depth_out.grid_mapping = mapping.name
  if lon is not None:
    lake_depth_out.coordinates = "lat lon"
  
  #lake_depth_filtered_out = ncOut.createVariable('lake_depth_filtered','f4', ['t','y','x'], fill_value=missing_value)
  #lake_depth_filtered_tmp = lake_depth_filtered.copy()
  #lake_depth_filtered_tmp[np.isnan(lake_depth_filtered)] = missing_value
  #lake_depth_filtered_out[:] = lake_depth_filtered_tmp[:,:]
  #lake_depth_filtered_out.units = "m"

  ncTopo.close()
  ncOut.close()
  print ("Written results to file "+fOut+" !")

def computeOceanMask(topg, thk, sea_level, alpha, shape):

  hgr = topg + thk
  sl = sea_level.copy()
  invalid_sl = np.isnan(sea_level)
  sl[invalid_sl] = topg[invalid_sl]
  hfl = sl + alpha * thk
  
  is_floating = hfl > hgr

  mask = np.zeros(shape)
  mask[is_floating]  = 1

  return mask

def getNcVarName(nc, var_names):
  if type(var_names) is not list:
    var_names = [var_names]

  name = None
  for var_name in var_names:
    try:
      name = var_name
      nc.variables[name]
    except:
      name = None

    if name is not None:
      break

  return name


def getNcVarSlice(nc, varname = "z", shape = None):

  name = getNcVarName(nc, varname)

  try:
    var = nc.variables[name]
    data = var[:,:]
  except:
    print("-" + str(varname) + " not found in file.")
    raise

  if shape is not None:
    if shape != data.shape:
      raise ValueError("Dimensions of "+name+ "do not match required dimensions.")

  return data.astype("double")




def main():
  options = parse_args()

  if options.lib is not None:
    import sys
    for p in options.lib[:]:
      print("Add path "+p+" to PYTHONPATH!")
      sys.path.append(p)

  FillLakes(options.year, options.topo, options.topo_filtered, options.inDir, options.output, options.sl, options.dz, options.zMin, options.zMax, options.rhoi, options.rhos, options.rhof, options.thk_if, options.ms)

def parse_args():
  from argparse import ArgumentParser
  import os

  #############################################################################################
  ####Set defaults   ##########################################################################
  #############################################################################################
  dataset_name="rtopo2" #"etopo1" 
  
  #default_input_dir = "."
  default_input_dir = "/scratch/users/shinck/IceModelling/Evan_13"

  #If set to None, default will be "input-dir/dataset_name"
  #default_topo_dir = None
  default_topo_dir = "/scratch/users/shinck/IceModelling/Evan_13/"+dataset_name

  #If set to None, default will be "input-dir/lakes"
  #default_output_dir = None 
  default_output_dir = "/scratch/users/shinck/IceModelling/Evan_13/lakes"
  
  default_dz = 10
  #If set to None, filling will be done from lowest point of topography to highest point!
  default_zMin = 0
  default_zMax = 1500
  
  default_sl = 0
  default_rho_i = 910.
  default_rho_s = 1027.
  default_rho_f = 1000.
  
  default_thk_if = 10.
  #############################################################################################

  parser = ArgumentParser()
  parser.description = "Fill lakes"
  parser.add_argument("-y", "--year",  dest="year",  required=True, help="Year of time-slice")
  parser.add_argument("-i", "--input-dir", dest="inDir", help="Directory that contains input data", default=default_input_dir, type=lambda x: os.path.abspath(x))
  parser.add_argument("-f", "--filter_width", dest="filterWidth", help="Filter width [km]", type=int)
  parser.add_argument("-t", "--topo", dest="topo", help="Directory or path of topography file", default=default_topo_dir, metavar="FILE", type=lambda x: os.path.abspath(x))
  parser.add_argument("-tf", "--topo_filtered", dest="topo_filtered", help="Directory or path of filtered topography file", default=default_topo_dir, metavar="FILE", type=lambda x: os.path.abspath(x))
  parser.add_argument("-o", "--output", dest="output", help="Output directory or file", default=default_output_dir, metavar="FILE", type=lambda x: os.path.abspath(x))
  parser.add_argument('-sl', "--sea-level", dest="sl", help="scalar sea-level", default=default_sl, type=float)
  parser.add_argument('-dz', "--lake_level_spacing", dest="dz", help="Lake level spacing", default=default_dz, type=float)
  parser.add_argument('-zMin', "--lake_level_min", dest="zMin", help="Lowest lake level", default=default_zMin, type=float)
  parser.add_argument('-zMax', "--lake_level_max", dest="zMax", help="Highest lake level", default=default_zMax, type=float)
  parser.add_argument('-rho_i', "--ice_density", dest="rhoi", help="Density of ice", default=default_rho_i, type=float)
  parser.add_argument('-rho_s', "--sea_water_density", dest="rhos", help="Density of sea water", default=default_rho_s, type=float)
  parser.add_argument('-rho_f', "--fresh_water_density", dest="rhof", help="Density of fresh water", default=default_rho_f, type=float)
  parser.add_argument('-thk_if', "--icefree_thickness", dest="thk_if", help="Icefree thickness", default=default_thk_if, type=float)
  parser.add_argument('-ms','--setMarginSink', dest='ms', action='store_true', help="set margin of domain as sink")
  parser.add_argument('-nms','--not-setMarginSink', dest='ms', action='store_false', help="not set margin of domain as sink")
  parser.add_argument("-l", "--lib", nargs='*', dest="lib", help="lib folder", type=lambda x: os.path.abspath(x))
  parser.set_defaults(ms=True)

  options = parser.parse_args()

  if options.topo is None:
    options.topo = os.path.join(options.inDir, dataset_name)
  if os.path.isdir(options.topo):
    options.topo = os.path.join(options.topo, dataset_name+"_LIS_Evan.nc")
  if not os.path.isfile(options.topo):
    options.topo = None

  if options.topo_filtered is None:
    if os.path.isfile(options.topo):
      options.topo_filtered = os.path.dirname(options.topo)
    else:
      options.topo_filtered = os.path.join(options.inDir, dataset_name)
  if os.path.isdir(options.topo_filtered):
    options.topo_filtered = os.path.join(options.topo_filtered, dataset_name+"_LIS_Evan_filtered"+str(options.filterWidth)+"km.nc")
  if not os.path.isfile(options.topo_filtered):
    options.topo_filtered = None

  if options.output is None:
    options.output = os.path.join(options.inDir, "lakes")
    if not os.path.isdir(options.output):
      os.mkdir(options.output)
  if os.path.isdir(options.output):
    oname = str(options.year)+"_lakes"
    if options.filterWidth is None:
      if options.topo_filtered is None:
        oname = oname + "_unfiltered"
    else:
        oname = oname + "_filtered"+str(options.filterWidth)+"km"
    oname = oname + ".nc"
    options.output = os.path.join(options.output, oname)
  if (not os.path.isdir(os.path.dirname(options.output)) or not options.output.endswith('.nc')):
    options.output = None

  return options



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

