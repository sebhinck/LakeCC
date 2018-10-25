# -*- mode: cython -*-

cdef extern from "LakeLevel_ConnectedComponents.hh":
    cdef cppclass LakeLevelCC:
        LakeLevelCC(unsigned int n_rows, unsigned int n_cols, double *usurf, double *thk, double *floatation_level, double *mask_run, double d_rho, double ice_free_thickness) except +
        void fill2Level(double Level)
        void floodMap(double zMin, double zMax, double dz)

cdef extern from "SeaLevel_ConnectedComponents.hh":
    cdef cppclass SeaLevelCC:
        SeaLevelCC(unsigned int n_rows, unsigned int n_cols, double *usurf, double *thk, double *floatation_level, double *mask_run, double d_rho, double ice_free_thickness) except +
        void fill2SeaLevel(double SeaLevel)