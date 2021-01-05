import os
import sys
import shutil
import numpy as np
import nibabel as nib
from subprocess import call
import ants

#Function to compute affine registration between moving (low res scan) and fixed (high res scan that you are registering all other sequences to) volume
def register_volume_slicer(moving_volume, fixed_volume, output_volume=None, transform_mode='useMomentsAlign', transform_type='Rigid,ScaleVersor3D,ScaleSkewVersor3D,Affine', interpolation_mode='BSpline', sampling_percentage=0.2, output_transform=False, slicer_dir='/opt/Slicer-4.8.1-linux-amd64/Slicer'):
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
        if output_transform:
            output_transform = '--outputTransform ' + output_volume.split('.nii')[0] + '_transformation_matrix.txt'
        else:
            output_transform=''
        affine_registration_command = [slicer_dir,'--launch', 'BRAINSFit', '--fixedVolume', '"' + fixed + '"', '--movingVolume', '"' + moving + '"', '--transformType', transform_type, '--initializeTransformMode', transform_mode, '--interpolationMode', interpolation_mode, '--samplingPercentage', str(sampling_percentage), output_transform, '--outputVolume', output_volume]
        call(' '.join(affine_registration_command), shell=True)
        return output_volume,output_transform

# apply transformation matrix to register
def register_transform_slicer(moving_volume,fixed_volume,transform_matrix,output_volume=None,slicer_dir='/opt/Slicer-4.8.1-linux-amd64/Slicer'):
    if type(moving_volume) == str:
        moving_volume = [moving_volume]
    if type(fixed_volume) == str:
        fixed_volume = [fixed_volume]
    if len(moving_volume) != len(fixed_volume) and len(fixed_volume) != 1:
        raise ValueError("Lists must be same size for Pairwise registration")
    if len(fixed_volume) == 1:
        fixed_volume = fixed_volume * len(fixed_volume)
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
        apply_transform_command= [slicer_dir,'--launch','ResampleScalarVectorDWIVolume',moving,output_volume,'-R',fixed,'-f',transform_matrix]
        call(' '.join(apply_transform_command), shell=True)
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

def register_volume_flirt(moving_volume,fixed_volume,output_volume=None):
    if output_volume is None:
        # ASSUMES that the path contains files where "-" seperates words
        # TODO make it more generalizable for files without the expected "STUDY_##-VISIT_##-..."
        output_volume = moving_volume.split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed_volume).split('-')[2:])
    if os.path.isdir(output_volume):
        output_volume = output_volume + '/' + os.path.basename(moving_volume).split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed_volume).split('-')[2:])
        if not os.path.basename(fixed_volume).split('-')[2:]:
            output_volume = output_volume + '/' + os.path.basename(moving_volume).split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed_volume).split('-')[1:])

    call('flirt -in ' + moving_volume + ' -ref ' + fixed_volume + ' -out ' + output_volume,shell=True)

def register_volume_antspy(moving_volume,fixed_volume,output_prefix="",transform_mode='SyN',initial_transform=None):
    ants.registration(ants.image_read(fixed_volume),ants.image_read(moving_volume),outprefix=output_prefix,verbose=True,typeoftransform=transform_mode,initial_transform=initial_transform)

def register_make_transform_ants(moving_volume,fixed_volume,output_volume=None,out_transform='matrix',transform_mode1='Rigid[0.1]',transform_mode2='Affine[0.1]',mask1='',mask2='',initial_transform=None,dimensionality='3',flot='0',interpolation='BSpline',convergence='[1000x500x250x1,1e-6,15]',smoothing_sigmas='3x2x1x0vox',shrink_factors='8x4x2x1',verbose='0'):
    ANTs_directory = '/home/kwl16/Projects/MPRAGE_r_DSC_pipelinev9/Third_version_consolidated/ants_bin/'
    # command = [ANTsDirectory 'antsRegistration ', ...
#     '--dimensionality 3 ', ...
#     '--float 0 ', ...
#     '--output transform_', identifier, '_ ', ...
#     '--interpolation Linear ', ...
#     '--transform Rigid[0.1] ', ... 
#     '--metric ', sprintf('MI[%s,%s,1,32,Regular,1]', fixedFilePath, movingFilePath), ' ', ...
#     '--convergence [1000x500x250x1,1e-6,15] ', ...
#     '--smoothing-sigmas 3x2x1x0vox ', ...
#     '--shrink-factors 8x4x2x1 ', ...
#     '--transform Affine[0.1] ', ... 
#     '--metric ', sprintf('MI[%s,%s,1,32,Regular,1]', fixedFilePath, movingFilePath), ' ', ...
#     '--convergence [1000x500x250x1,1e-6,15] ', ...
#     '--smoothing-sigmas 3x2x1x0vox ', ...
#     '--shrink-factors 8x4x2x1 ', ...
#     '--masks [' mask1 ', ' mask2 '] ', ...
# 	'--verbose 0']
    call(ANTs_directory + 'antsRegistration'
    ' --dimensionality ' + dimensionality + 
    ' --float ' + flot + 
    ' --output transform_' + out_transform + '_' + 
    ' --interpolation ' + interpolation + 
    ' --transform ' + transform_mode1 + 
    ' --metric ' + 'MI[' +fixed_volume + ',' + moving_volume + ',1,32,Regular,1]' + 
    ' --convergence ' + convergence + 
    ' --smoothing-sigmas ' + smoothing_sigmas + 
    ' --shrink-factors ' + shrink_factors + 
    ' --transform ' + transform_mode2 + 
    ' --metric ' + 'MI[' +fixed_volume + ',' + moving_volume + ',1,32,Regular,1]' + 
    ' --convergence ' + convergence + 
    ' --smoothing-sigmas ' + smoothing_sigmas + 
    ' --shrink-factors ' + shrink_factors + 
    ' --masks [' + mask1 + ', ' + mask2 + ']' + 
    ' --verbose ' + verbose,shell=True)
    if output_volume is None:
        output_volume = moving_volume.split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed_volume).split('-')[2:])
    if os.path.isdir(output_volume):
        output_volume = output_volume + '/' + os.path.basename(moving_volume).split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed_volume).split('-')[2:])
        if not os.path.basename(fixed_volume).split('-')[2:]:
            output_volume = output_volume + '/' + os.path.basename(moving_volume).split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed_volume).split('-')[1:])
    if os.path.isfile(os.path.dirname(output_volume) + '/' + 'transform_' + out_transform + '_0GenericAffine.mat'):
        os.remove(os.path.dirname(output_volume) + '/' + 'transform_' + out_transform + '_0GenericAffine.mat')
    shutil.move('transform_' + out_transform + '_0GenericAffine.mat',os.path.dirname(output_volume))
    return os.path.dirname(output_volume) + '/' + 'transform_' + out_transform + '_0GenericAffine.mat'

def register_transform_ants(moving_volume,fixed_volume,transformation,output_volume,dimensionality='3',interpolation='Linear',verbose='0'):
    ANTs_directory = '/home/kwl16/Projects/MPRAGE_r_DSC_pipelinev9/Third_version_consolidated/ants_bin/'
    
    if output_volume is None:
        output_volume = moving_volume.split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed_volume).split('-')[2:])
    if os.path.isdir(output_volume):
        output_volume = output_volume + '/' + os.path.basename(moving_volume).split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed_volume).split('-')[2:])
        if not os.path.basename(fixed_volume).split('-')[2:]:
            output_volume = output_volume + '/' + os.path.basename(moving_volume).split('.nii')[0] + "_r_" + '-'.join(os.path.basename(fixed_volume).split('-')[1:])
    call(ANTs_directory + 'antsApplyTransforms' + 
    ' --dimensionality ' + dimensionality + 
    ' --input ' + moving_volume + 
    ' --reference-image ' + fixed_volume + 
    ' --output ' + output_volume + 
    ' --interpolation ' + interpolation +
    ' --transform ' + transformation +
    ' --verbose ' + verbose,
    shell=True)

# write function to apply trnasformation to the antsregistration apply
