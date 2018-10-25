# -*- mode: cython -*-
cimport numpy as np
import numpy as np
cimport LakeModel_ConnectedComponents

ctypedef np.float64_t double_t
ctypedef np.int64_t int_t

def LakeModelCC(np.ndarray[dtype=double_t, ndim=2, mode='c'] topg,
                np.ndarray[dtype=double_t, ndim=2, mode='c'] thk,
                np.ndarray[dtype=double_t, ndim=2, mode='c'] ocean_mask,
                rho_i, rho_w, ice_free_thickness = 10, setMarginSink=True,
                dz=10., zMin=None, zMax=None):

    cdef np.ndarray[dtype=double_t, ndim=2, mode='c'] m_floatation_level
    cdef np.ndarray[dtype=double_t, ndim=2, mode='c'] m_topg
    cdef np.ndarray[dtype=double_t, ndim=2, mode='c'] m_thk
    cdef np.ndarray[dtype=double_t, ndim=2, mode='c'] m_mask_run

    cdef unsigned int n_rows, n_cols
    cdef double topgMax, topgMin

    n_rows = topg.shape[0]
    n_cols = topg.shape[1]

    topgMax = topg.max()
    topgMin = topg.min()

    m_topg = topg.copy()
    m_thk  = thk.copy()

    if ocean_mask is not None:
        m_mask_run = ocean_mask.copy()
    else:
        m_mask_run = np.zeros_like(topg)

    if setMarginSink:
        m_mask_run[ 0,  :] = 1
        m_mask_run[-1,  :] = 1
        m_mask_run[: ,  0] = 1
        m_mask_run[: , -1] = 1

    m_floatation_level = np.zeros_like(topg)
    m_floatation_level[:,:] = <double_t>np.nan

    drho = rho_i/rho_w
    ice_free_thickness = ice_free_thickness

    if zMin is None:
        zMin = topgMin
    if zMax is None:
        zMax = topgMax

    cdef LakeModel_ConnectedComponents.LakeLevelCC* c_LakeModelCC
    c_LakeModelCC = new LakeModel_ConnectedComponents.LakeLevelCC(n_rows, n_cols,
                                                                  &m_topg[0,0],
                                                                  &m_thk[0,0],
                                                                  &m_floatation_level[0,0],
                                                                  &m_mask_run[0,0],
                                                                  drho,
                                                                  ice_free_thickness)
    c_LakeModelCC.floodMap(zMin, zMax, dz)

    del c_LakeModelCC

    return m_floatation_level



def SeaLevelModelCC(np.ndarray[dtype=double_t, ndim=2, mode='c'] topg,
                    np.ndarray[dtype=double_t, ndim=2, mode='c'] thk,
                    np.ndarray[dtype=double_t, ndim=2, mode='c'] mask_run,
                    rho_i, rho_w, ice_free_thickness = 10, sl = 0.0):

    cdef np.ndarray[dtype=double_t, ndim=2, mode='c'] m_floatation_level
    cdef np.ndarray[dtype=double_t, ndim=2, mode='c'] m_topg
    cdef np.ndarray[dtype=double_t, ndim=2, mode='c'] m_thk
    cdef np.ndarray[dtype=double_t, ndim=2, mode='c'] m_mask_run

    cdef unsigned int n_rows, n_cols

    n_rows = topg.shape[0]
    n_cols = topg.shape[1]

    m_topg = topg.copy()
    m_thk  = thk.copy()
    m_mask_run = mask_run.copy()

    m_floatation_level = np.zeros([n_rows, n_cols])
    m_floatation_level[:,:] = <double_t>np.nan

    drho = rho_i/rho_w
    ice_free_thickness = ice_free_thickness

    cdef LakeModel_ConnectedComponents.SeaLevelCC* c_SeaLevelModelCC
    c_LakeModelCC = new LakeModel_ConnectedComponents.SeaLevelCC(n_rows, n_cols,
                                                                 &m_topg[0,0],
                                                                 &m_thk[0,0],
                                                                 &m_floatation_level[0,0],
                                                                 &m_mask_run[0,0],
                                                                 drho,
                                                                 ice_free_thickness)
    c_LakeModelCC.fill2SeaLevel(sl)

    del c_SeaLevelModelCC

    return m_floatation_level
