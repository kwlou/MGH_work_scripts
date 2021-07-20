import sys
import os
import nibabel as nib
from glob import glob
import numpy as np
from subprocess import call

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

def roi_overlay(reference,roi,fill_value=0):
    """
    takes 2 paths, or nib_variables, or np.arrays, to overlay the roi on top of a reference image, returns resulting data 
    maybe implement returning nib object instead using nib.Nifti1Image()   
    """
    if isinstance(roi,str):
        roi = nib.load(roi)
    if isinstance(reference,str):
        reference = nib.load(reference)
    if isinstance(roi,nib.nifti1.Nifti1Image):
        roi_data = roi.get_fdata()
    if isinstance(reference,nib.nifti1.Nifti1Image):
        reference_data = reference.get_fdata()
    if isinstance(roi,np.ndarray):
        roi_data = np.copy(roi)
    if isinstance(reference,np.ndarray):
        reference_data = reference
    # set all non zero roi's to equal 0 and all 0's to equal 1 to represent mask
    roi_data[np.nonzero(roi_data)] = 1
    roi_data = 1 - roi_data
    # mask to remove all 1's in roi from reference image 
    reference_masked = np.ma.masked_array(reference_data,roi_data,fill_value=fill_value).filled()
    return reference_masked

def mask_compare(array_1,array_2,matching_nums=0):
    """
    Takes two arrays and finds where matching_nums values are mutual (the same)
    returns an array of indicies of overlap
    """
    array_1_roi = array_1 == matching_nums
    array_2_roi = array_2 == matching_nums
    return np.logical_and(array_1_roi,array_2_roi)

def remove_slices(image,axis=2,n_low_cutoff=6,n_high_cutoff=6,output='_slices_cutoff'):
    """
    takes an image and removes slices from the axis of choice, so if the top or bottom of the axial is non-real data messing with registration
    returns path to new_nib
    """
    image_nib = nib.load(image)
    image_data = image_nib.get_fdata()
    # doesnt work because you need to knowthe upper range, need some len of axis=x
    # image_data = image_data.take(indices=range(3,20),axis=2)
    slices = [slice(None)] * len(np.shape(image_data))
    slices[axis] = slice(n_low_cutoff,-n_high_cutoff)
    image_data = image_data[tuple(slices)]
    new_image_nib = nib.Nifti1Image(image_data,image_nib.affine,header=image_nib.header)
    output_path = image.split('.nii')[0]+output+'.nii'+''.join(image.split('.nii')[1:])
    nib.save(new_image_nib,output_path)
    return output_path

def skullstripping_robex(image,output):
    call('/home/kwl16/Projects/Carlsbad_Pipeline_docker/DeepMets/shared_software/ROBEX/runROBEX.sh ' + image + ' ' + output,shell=True)

def skullstripping_fsl(image,output,fractional_intensity=0.5,gradient=0):
    if type(fractional_intensity) != str:
        fractional_intensity = str(fractional_intensity)
    if type(gradient) != str:
        gradient = str(gradient)
    call('fsl5.0-bet2 ' + image + ' ' + output + ' -f ' + fractional_intensity + ' -g ' + gradient,shell=True)


