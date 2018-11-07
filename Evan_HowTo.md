# Instructions for Evan

1. Get PismGrids from my Github account: `git@github.com:sebhinck/PismGrids.git`
2. Define `${GRID_FOLDER}` and `${ETOPO_FOLDER}`
  run `./run_create_domain_grid.sh LIS_Evan 5 ${GRID_FOLDER`, to create grid files needed for the projection   
  **NOTE: This script needs the file nc2cdo.py from PISM. This can be found in the PISM-bin folder**

3. Download & convert Etopo1 Dataset:
    ```
    wget -nc https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/cell_registered/netcdf/ETOPO1_Bed_c_gmt4.grd.gz -P ${ETOPO_FOLDER}
    gunzip ${ETOPO_FOLDER}/ETOPO1_Bed_c_gmt4.grd.gz
    cdo -f nc copy ${ETOPO_FOLDER}/ETOPO1_Bed_c_gmt4.grd ${ETOPO_FOLDER}/ETOPO1_Bed_c_gmt4.nc
    ```
4. Extract Northern hemisphere to reduce file size: 
    ```
    cdo sellonlatbox,-180,180,23,90 ${ETOPO_FOLDER}/ETOPO1_Bed_c_gmt4.nc ${ETOPO_FOLDER}/etopo1_NH.nc
    ```
    
5. Create bilinear interpolation weights:
    ```
    cdo -P 3 genbil,${GRID_FOLDER}/LIS_Evan/pismr_LIS_Evan_5km.griddes ${ETOPO_FOLDER}/etopo1_NH.nc ${ETOPO_FOLDER}/etopo1toLIS_Evan.nc
    ```
6. (Minimum) Filter Etopo1 dataset at desired filter width:
    ```
    gmt grdfilter ${ETOPO_FOLDER}/etopo1_NH.nc -G${ETOPO_FOLDER}/etopo1_NH_filtered**X**km.nc -Fl**X** -D4 -V
    ```
    i.e. `gmt grdfilter ${ETOPO_FOLDER}/etopo1_NH.nc -G${ETOPO_FOLDER}/etopo1_NH_filtered20km.nc -Fl20 -D4 -V`
    
7. Interpolate filtered
    ```
    cdo remap,${GRID_FOLDER}/LIS_Evan/pismr_LIS_Evan_5km.griddes,${ETOPO_FOLDER}/etopo1toLIS_Evan.nc ${ETOPO_FOLDER}/etopo1_NH_filtered**X**km.nc ${ETOPO_FOLDER}/etopo1_LIS_Evan_filtered**X**km.nc
    ```
    and unfiltered datasets onto chosen grid.
    ```
    cdo remap,${GRID_FOLDER}/LIS_Evan/pismr_LIS_Evan_5km.griddes,${ETOPO_FOLDER}/etopo1toLIS_Evan.nc ${ETOPO_FOLDER}/etopo1_NH.nc etopo1_LIS_Evan.nc
    ```

8. Get LakeCC tools from my github (this repository): `git@github.com:sebhinck/LakeCC.git`   
   Checkout branch `FillLakes_Evan`   
   Install it by running `make all`
    
9. Make sure to match the file name pattern given above.   
   You might want to adjust the default values for `input_dir`, `etopo_dir`, `output_dir`, ... in [FillLakes_Evan.py (in function "parse_args()" l.237ff)](https://github.com/sebhinck/LakeCC/blob/d51b8e5b23b89d51ac816dd0b7ca95c2d7e0017d/FillLakes_Evan.py#L237)  so that you don't have to specify it every time you run the tool.

10. Execute it with `./FillLakes_Evan.py -y YEAR -f FILTER_WIDTH ....`   
    Make sure that Data for `YEAR` is present in folder `input_dir` and that  `etopo1_LIS_Evan_filtered**FILTER_WIDTH**km.nc` is available in folder `etopo_dir`.  
    For a list of all options see `./FillLakes_Evan.py -h`
