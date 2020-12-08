# Resample image to match target image

import nibabel as nib
from glob import glob
import os
import sys
from subprocess import call
from datetime import datetime, date

# logic to find images to resample under list images
resample_dir='/qtim2/users/data/MEL/ANALYSIS/COREGISTRATION/'
images=glob(resample_dir+'*/*/*AUTO*')
target_images=[]

# logic for the target image selection
# for folder in glob(resample_dir+'*/'):
#     base_file = sorted(glob(folder+'*MEN*'),key=len)[0]
#     target_images.append(base_file)

for i in range(len(images)):
    path=os.path.dirname(images[i])
    target_images.append(sorted(glob(path+'/*'),key=len)[0])
    


def resample_to_target(input_image,target_image,output_file=None,interp_type='nn',module_name='ResampleScalarVectorDWIVolume',slicer_dir = '/opt/Slicer-4.8.1-linux-amd64/Slicer'):
    # if save_dir==None:
    #     save_dir=os.path.dirname(input_image)
    if output_file==None:
        output_file = input_image[:-7] + '_resampled.nii.gz'

    resample_scalar_volume_command = [slicer_dir,'--launch', module_name, '"' + input_image + '" "' + output_file + '"', '-i', interp_type, '-R', target_image]
    call(' '.join(resample_scalar_volume_command),shell=True)

def resample_spacing(input_image,output_file=None,interp_type='bspline',spacing='1,1,1',module_name='ResampleScalarVolume',slicer_dir = '/opt/Slicer-4.8.1-linux-amd64/Slicer'):
    # if save_dir==None:
    #     save_dir=os.path.dirname(input_image)
    if output_file==None:
        output_file = input_image[:-7] + '_resampled.nii.gz'

    resample_scalar_volume_command = [slicer_dir,'--launch', module_name, '"' + input_image + '" "' + output_file + '"', '-i', interp_type, '-s', spacing]
    call(' '.join(resample_scalar_volume_command),shell=True)


if __name__ == "__main__":
    resample_to_target(sys.argv[1],sys.argv[2],sys.argv[3])

