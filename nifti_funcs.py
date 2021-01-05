import sys
import os
import nibabel as nib
from glob import glob
import numpy as np


def volume_from_nifti(nib_variable):
    '''
    load in a nib object or path to nifti to return volume of non zero data using header info
    '''
    if type(nib_variable)==str:
        nib_variable=nib.load(nib_variable)
    voxel_dim = nib_variable.header['pixdim'][1:4]
    voxel_volume = voxel_dim[0]*voxel_dim[1]*voxel_dim[2]
    voxel_count = np.count_nonzero(nib_variable.get_fdata())
    return voxel_volume*voxel_count

def roi_overlay(roi,reference):
    """
    takes 2 paths, or nib_variables, to overlay the roi on top of a reference image, returns resulting data 
    maybe implement returning nib object instead using nib.Nifti1Image()   
    """
    if type(roi)==str:
        roi = nib.load(roi)
    if type(reference)==str:
        reference = nib.load(reference)
    roi_data = roi.get_fdata()
    reference_data = reference.get_fdata()
    # set all non zero roi's to equal 0 and all 0's to equal 1 to represent mask
    roi_data[np.nonzero(roi_data)] = 1
    roi_data = 1 - roi_data
    # mask to remove all 1's in roi from reference image 
    reference_masked = np.ma.masked_array(reference_data,roi_data,fill_value=0).filled()
    return reference_masked

def remove_slices(image,axis=2,n_low_cutoff=3,n_high_cutoff=3,output='_slices_cutoff'):
    """
    takes an image and removes slices from the axis of choice, so if the top or bottom of the axial is non-real data messing with registration
    returns path to new_nib
    """
    image = nib.load(image)
    image_data = image.get_fdata()
    # doesnt work because you need to knowthe upper range, need some len of axis=x
    # image_data = image_data.take(indices=range(3,20),axis=2)
    slices = [slice(None)] * len(np.shape(image_data))
    slices[axis] = slice(n_low_cutoff,-n_high_cutoff)
    image_data = image_data[tuple(slices)]
    new_image_nib = nib.Nifti1Image(image_data,image.affine,header=image.header)
    output_path = image.split('.nii')[0]+output+image.split('.nii')[1:]
    nib.save(output_path)
    return output_path




        
    