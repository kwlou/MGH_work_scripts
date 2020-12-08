import sys
import os
import nibabel as nib
from glob import glob
import numpy as np

def volume_from_nifti(nib_variable):
    voxel_dim = nib_variable.header['pixdim'][1:4]
    voxel_volume = voxel_dim[0]*voxel_dim[1]*voxel_dim[2]
    voxel_count = np.count_nonzero(nib_variable.get_fdata())
    return voxel_volume*voxel_count

