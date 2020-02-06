#coreg utils
import subprocess
from glob import glob
import os
import re 

ini_str='BAV_03-VISIT_04-DTI_FA_r_T2.nii.gz'

# Finding nth occurrence of substring 
inilist = [m.start() for m in re.finditer(r"/", ini_str)] 

slicer_dir='/opt/Slicer-4.8.1-linux-amd64/Slicer'

def resample_scan(in_volume,output_volume,spacing='1,1,1',slicer_directory=slicer_dir,interpType='bspline'):
    '''
    Resample input image, isotropic by default
    '''
    resample_scalar_volume_command = [slicer_directory,'--launch', 'ResampleScalarVolume', '"' + in_volume + '" "' + output_volume + '"', '-i', interpType, '-s', spacing]
    subprocess.call(' '.join(resample_scalar_volume_command), shell=True)


def coreg_scan(fixed_volume,moving_volume,output_volume=None,module='BRAINSFit',slicer_directory=slicer_dir,transform_type='Rigid,ScaleVersor3D,ScaleSkewVersor3D,Affine',
    initialize_transform_mode='useMomentsAlign',interpolation_mode='Linear',sampling_percentage='.02'):

    if output_volume is None:
        init_index=0
        moving_prefix_index=0
        fixed_prefix_index=0
        if '/' in fixed_volume:
            list_of_occurences = [m.start() for m in re.finditer(r"/", fixed_volume)]
            init_index+= list_of_occurences[-1]
            fixed_prefix_index=list_of_occurences[-1]
        if '/' in moving_volume:
            list_of_occurences = [m.start() for m in re.finditer(r"/", moving_volume)]
            moving_prefix_index= list_of_occurences[-1]            
        if '-' in fixed_volume:
            list_of_occurences = [m.start() for m in re.finditer(r"-", fixed_volume[init_index:])]
            init_index += list_of_occurences[1] + 1
        output_volume='{0}{1}_r_{2}'.format(fixed_volume[:fixed_prefix_index],moving_volume[moving_prefix_index:moving_volume.find('.nii')],fixed_volume[init_index:])

    coreg_command=[slicer_dir,'--launch',module,'--fixedVolume',fixed_volume,'--movingVolume',moving_volume,'--transformType',transform_type,'--initializeTransformMode',
    initialize_transform_mode,'--interpolationMode',interpolation_mode,'--outputVolume','"' + output_volume + '"','--samplingPercentage',sampling_percentage]
    subprocess.call(' '.join(coreg_command),shell=True)