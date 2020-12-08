import os
import sys
import shutil
import numpy as np
import nibabel as nib
from subprocess import call

#Function to compute affine registration between moving (low res scan) and fixed (high res scan that you are registering all other sequences to) volume
def register_volume_slicer(moving_volume, fixed_volume, output_volume=None, transform_mode='useMomentsAlign', transform_type='Rigid,ScaleVersor3D,ScaleSkewVersor3D,Affine', interpolation_mode='BSpline', sampling_percentage=0.2, output_transform_filename=False, slicer_dir='/opt/Slicer-4.8.1-linux-amd64/Slicer'):
    #setting up and organizing inputs
    if type(moving_volume) == str:
        moving_volume = [moving_volume]
    if type(fixed_volume) == str:
        fixed_volume = [fixed_volume]
    if len(moving_volume) != len(fixed_volume) and len(fixed_volume) != 1:
        raise ValueError("Lists must be same size for Pairwise registration")
    if len(fixed_volume) == 1:
        fixed_volume = fixed_volume * len(fixed_volume)
    # registering using slicer
    for moving, fixed in zip(moving_volume,fixed_volume):
        if output_volume is None:
            # ASSUMES that the path contains files where "-" seperates words
            # TODO make it more generalizable for files without the expected "STUDY_##-VISIT_##-..."
            output_volume = moving.split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed).split('-')[2:])
        if os.path.isdir(output_volume):
            output_volume = output_volume + '/' + os.path.basename(moving).split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed).split('-')[2:])
            if not os.path.basename(fixed).split('-')[2:]:
                output_volume = output_volume + '/' + os.path.basename(moving).split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed).split('-')[1:])
        # not saving the transform matrix by default
        if output_transform_filename:
            output_transform_filename = output_volume.split('.nii')[0] + '.txt'
        else:
            output_transform_filename=''
        affine_registration_command = [slicer_dir,'--launch', 'BRAINSFit', '--fixedVolume', '"' + fixed + '"', '--movingVolume', '"' + moving + '"', '--transformType', transform_type, '--initializeTransformMode', transform_mode, '--interpolationMode', interpolation_mode, '--samplingPercentage', str(sampling_percentage), output_transform_filename, '--outputVolume', output_volume]
        call(' '.join(affine_registration_command), shell=True)
        return output_volume

        
def resample_volume_using_reference(moving_volume, fixed_volume, output_volume=None, interp_type='nn', slicer_dir='/opt/Slicer-4.8.1-linux-amd64/Slicer'):
    #resampling module
    module_name = 'ResampleScalarVectorDWIVolume'
    if output_volume is None:
        output_volume = moving_volume
    if interp_type == 'nearestNeighbor':
        interp_type = 'nn'
    else:
        interp_type = 'bs'
    resample_scalar_volume_command = [slicer_dir,'--launch', module_name, '"' + moving_volume + '" "' + output_volume + '"', '-i', interp_type, '-R', fixed_volume]
    call(' '.join(resample_scalar_volume_command), shell=True)
    #return created file names
    return output_filenames
