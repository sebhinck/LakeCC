# -*- mode: cython -*-
cimport numpy as np
import numpy
from cython.view cimport array as cvarray
cimport LakeModel_ConnectedComponents

ctypedef np.float64_t double_t
ctypedef np.int64_t int_t

cdef class LakeModelCC:

    cdef double_t[:,:] topg
    cdef double_t[:,:] thk
    cdef double_t[:,:] floatation_level
    cdef double_t topgMax, topgMin
    cdef double_t[:,:] mask_run
    cdef int pism_mask_free_rock
    cdef int pism_mask_grounded
    cdef int pism_mask_floating
    cdef int pism_mask_free_ocean
    cdef int pism_mask_lake
    cdef double drho
    
    cdef LakeModel_ConnectedComponents.LakeLevelCC* c_LakeModelCC      # hold a C++ instance which we're wrapping
    def __cinit__(self, np.ndarray[dtype=double_t, ndim=2, mode='c'] topg, np.ndarray[dtype=double_t, ndim=2, mode='c'] thk, np.ndarray[dtype=double_t, ndim=2, mode='c'] ocean_mask, rho_i, rho_w, setMarginSink=True):
        
        cdef unsigned int n_rows, n_cols
        n_rows = topg.shape[0]
        n_cols = topg.shape[1]

        self.topg = topg.copy()
        self.topgMax = topg.max()
        self.topgMin = topg.min()
        self.thk = thk.copy()
        self.floatation_level = cvarray(shape=(n_rows, n_cols), itemsize = sizeof(double_t), format="d")
        self.floatation_level[:,:] = <double_t>numpy.nan

        if ocean_mask is not None:
            self.mask_run = ocean_mask.copy()
        else:
            self.mask_run = numpy.zeros_like(topg)
            
        if setMarginSink:
            self.mask_run[ 0,  :] = 1
            self.mask_run[-1,  :] = 1
            self.mask_run[: ,  0] = 1
            self.mask_run[: , -1] = 1
                    
        self.drho = rho_i/rho_w
        
        self.c_LakeModelCC = new LakeModel_ConnectedComponents.LakeLevelCC(n_rows, n_cols, &self.topg[0,0], &self.thk[0,0], &self.floatation_level[0,0], &self.mask_run[0,0], self.drho)
        
    def __dealloc__(self):
        del self.c_LakeModelCC
                
    def gettopg(self):
        return numpy.asarray(self.topg)
    
    def getThk(self):
        return numpy.asarray(self.thk)
    
    def getFloatationLevel(self):
        return numpy.asarray(self.floatation_level)
    
    def getMaskRun(self):
        return numpy.asarray(self.mask_run).astype("int")
                   
    def fill2Level(self, double Level=0.0):
            
        self.c_LakeModelCC.fill2Level(Level)
        
    def fillLakes(self, dh=10., Min=None, Max=None):
        
        if Min is None:
            Min = self.topgMin
        if Max is None:
            Max = self.topgMax        

        self.c_LakeModelCC.floodMap(Min, Max, dh)
        
        
cdef class SeaLevelModelCC:

    cdef double_t[:,:] topg
    cdef double_t[:,:] thk
    cdef double_t[:,:] floatation_level
    cdef double_t[:,:] mask_run
    cdef double drho
    
    cdef LakeModel_ConnectedComponents.SeaLevelCC* c_SeaLevelModelCC      # hold a C++ instance which we're wrapping
    def __cinit__(self, np.ndarray[dtype=double_t, ndim=2, mode='c'] topg, np.ndarray[dtype=double_t, ndim=2, mode='c'] thk, np.ndarray[dtype=double_t, ndim=2, mode='c'] mask_run, rho_i, rho_w):
      
        cdef unsigned int n_rows, n_cols
        n_rows = topg.shape[0]
        n_cols = topg.shape[1]
        
        self.topg = topg.copy()
        self.thk = thk.copy()
        self.mask_run = mask_run.copy()
        self.floatation_level = thk.copy()
        self.floatation_level[:,:] = <double_t>numpy.nan

        self.drho = rho_i/rho_w
        
        self.c_SeaLevelModelCC = new LakeModel_ConnectedComponents.SeaLevelCC(n_rows, n_cols, &self.topg[0,0], &self.thk[0,0], &self.floatation_level[0,0], &self.mask_run[0,0], self.drho)
        
    def __dealloc__(self):
        del self.c_SeaLevelModelCC
                
    def gettopg(self):
        return numpy.asarray(self.topg)
    
    def getThk(self):
        return numpy.asarray(self.thk)
    
    def getFloatationLevel(self):
        return numpy.asarray(self.floatation_level)
         
    def fill2SeaLevel(self, double SeaLevel=0.0):
            
        self.c_SeaLevelModelCC.fill2SeaLevel(SeaLevel)
        
        
