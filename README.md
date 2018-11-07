# LakeCC
Standalone Python module to identify lake basins

![figure](https://github.com/sebhinck/LakeCC/blob/master/examples/GreatLakes.png)

The algorithm is based on the Connected Components algorithm and was inspired by the work of Constantine Khrulev (https://github.com/ckhroulev/connected-components).

->Evan, a description how you prepare everything can be found [here](Evan_HowTo.md)

## Building
Run `make all` in base directory.

## Usage
This python module can be imported by running `import LakeCC` in python.
It basically consits of two submudules: LakeModelCC and SeaLevelModelCC, that are both based on the same algorithm. SeaLevelModelCC is used to compute the spatial sea-level that is needed used in LakeModelCC as a sink condition to determine if the lakes overflow.

Additionally to the python interface there is also a wrapper `FillLakes.py` that reads netCDF files, calles the python interface and saves the results to a netCDF file.

In the following the python interface, the wrapper and an example are shortly described.

## Python Interface
### SeaLevelModelCC
This model needs some input:
* topography - spatial map of bedrock
* ice_thickness - spatial map of ice thickness
* sl_mask - a map that is 1 at cells that are known to be ocean, and zero otherwise. A mask that is only 1 at the margin would for example result in ocean basins that need to be connected to the margin of the domain, whereas cells below the sea-level that are cut off the ocean are not added to the ocean extent.
* rho_ice and rho_sea - density of ice and sea water, respectively
* ice_free_thickness - ice thickness threshold, below which a cell is considered as ice free
* scalar sea-level


### LakeModelCC
For initialization this model needs some input:
* topography - spatial map of bedrock
* ice_thickness - spatial map of ice thickness
* ocean_mask - a map that is 1 at ocean cells and zero otherwise. This map can easily be computed from the output of SeaLevelModelCC
* rho_ice and rho_fresh - density of ice and fresh water, respectively
* ice_free_thickness - ice thickness threshold, below which a cell is considered as ice free
* dz - step size between successive lake levels to be checked
* zMin - lowest lake level
* zMax - highest lake level


## FillLakes.py - Wrapper
This is short description of the wrapper around the python scripts. It reads and writes netCDF files and therefore simplifies the application of these tools. Here is a list of all options available:
```
usage: FillLakes.py [-h] -i FILE [-o FILE] [-sl SL] [-dz DZ] [-zMin ZMIN]
                    [-zMax ZMAX] [-rho_i RHOI] [-rho_s RHOS] [-rho_f RHOF]
                    [-thk_if THK_IF] [-tind TIND] [-ms] [-nms]

Fill lakes

optional arguments:
  -h, --help            show this help message and exit
  -i FILE, --input FILE
                        Input file
  -o FILE, --output FILE
                        Output file
  -sl SL, --sea-level SL
                        scalar sea-level
  -dz DZ, --lake_level_spacing DZ
                        Lake level spacing
  -zMin ZMIN, --lake_level_min ZMIN
                        Lowest lake level
  -zMax ZMAX, --lake_level_max ZMAX
                        Highest lake level
  -rho_i RHOI, --ice_density RHOI
                        Density of ice
  -rho_s RHOS, --sea_water_density RHOS
                        Density of sea water
  -rho_f RHOF, --fresh_water_density RHOF
                        Density of fresh water
  -thk_if THK_IF, --icefree_thickness THK_IF
                        Icefree thickness
  -tind TIND, --time-index TIND
                        index of time dimension
  -ms, --setMarginSink  set margin of domain as sink
  -nms, --not-setMarginSink
                        not set margin of domain as sink
```
Most options are pretty self-explaning.
By default this tool would take the domain's margin as a sink (i.e. a lake connected to the margin overflows), this can be disables by setting `--not-setMarginSink`.

It is important to mention that the variable names of the input files are important. Here is a list of all recognized fields:
* `topg` - *needed* - topography of bedrock
* `thk` - *optional* - ice thickness. If missing defaults to zero.
* `ocean_mask` - *optional*. Mask that is one at ocean cells, zero otherwise. If missing it is determined from the sea_level
* `sea_level` - *optional*. Spatial sea-level elevation. Invalid cells are excluded from the ocean extent. If missing it is calculated using SeaLevelModelCC.
* `sl_mask` - *optional*. Map that is 1 at cells that are known to be ocean, and zero otherwise. If missing it is set to 1 only at the margin of the domain.

## Examples
So far there is only one example: `examples/fill_great_lakes.sh`. The first run can take some time since it downloads the Etopo1 dataset (~500MB). From this global dataset the script crops (and filters) the area of the Great lakes and applies the `FillLakes.py` tool on it.
