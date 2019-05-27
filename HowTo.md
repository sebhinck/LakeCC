# This file describes how the data was prepared and the LakeCC model was applied for the publication

1. Get high-res PD topography dataset (e.g. [Rtopo2](https://doi.pangaea.de/10.1594/PANGAEA.856844) )

2. Extract Northern hemisphere to reduce file size: 
    ```
    cdo sellonlatbox,-180,180,23,90 ${RTOPO_FOLDER}/RTOPO2.nc ${RTOPO_FOLDER}/RTOPO2_NH.nc
    ```

3. (Minimum) Filter RTOPO2 dataset at desired filter width:
    ```
    gmt grdfilter ${RTOPO_FOLDER}/RTOPO2_NH.nc -G${RTOPO_FOLDER}/RTOPO2_NH_filtered**X**km.nc -Fl**X** -D4 -V
    ```

4. Interpolate filtered
    ```
    cdo remapbil,${GRIDDES} ${RTOPO_FOLDER}/RTOPO2_NH_filteredXkm.nc ${RTOPO_FOLDER}/RTOPO2_LIS_filtered**X**km.nc
    ```
    and unfiltered datasets onto chosen grid (described by ${GRIDDES}).
    ```
    cdo remapbil,${GRIDDES} ${RTOPO_FOLDER}/RTOPO2_NH.nc ${RTOPO_FOLDER}/RTOPO2_LIS.nc
    ```

5. Adapt default values and filename patterns to your needs in `parse_args()` in file `FillLakes_publication.py`.

6. Execute script `FillLakes_publication.py` with `./FillLakes_publication.py -y YEAR -f FILTER_WIDTH ....`   
    Make sure that Data for `YEAR` is present in folder `input_dir` and that  `RTOPO2_LIS_filteredXkm.nc` is available in folder `RTOPO_FOLDER`.  
    For a list of all options see `./FillLakes_publication.py -h`
