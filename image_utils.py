#coreg utils
import subprocess
from glob import glob
import os


slicer_dir='/opt/Slicer-4.8.1-linux-amd64/Slicer'

def resample_scan(in_volume,resampled_volume,spacing='1,1,1',slicer_directory=slicer_dir,interpType='bspline'):
    '''
    Resample input image, isotropic by default
    '''
    resample_scalar_volume_command = [slicer_directory,'--launch', 'ResampleScalarVolume', '"' + in_volume + '" "' + resampled_volume + '"', '-i', interpType, '-s', spacing]
    subprocess.call(' '.join(resample_scalar_volume_command), shell=True)


def coreg_scan(fixed_volume,moving_volume,output_volume,module='BRAINSFit',slicer_directory=slicer_dir,transform_type='Rigid,ScaleVersor3D,ScaleSkewVersor3D,Affine',
    initialize_transform_mode='useMomentsAlign',interpolation_mode='Linear',sampling_percentage='.02'):
    coreg_command=[slicer_dir,'--launch',module,'--fixedVolume',fixed_volume,'--movingVolume',moving_volume,'--transformType',transform_type,'--initializeTransformMode',
    initialize_transform_mode,'--interpolationMode',interpolation_mode,'--outputVolume',output_volume,'--samplingPercentage',sampling_percentage]
    subprocess.call(' '.join(coreg_command),shell=True)