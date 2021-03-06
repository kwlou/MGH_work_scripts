import nibabel as nib
import numpy as np
import os
from glob import glob
import math

from qtim_tools.qtim_utilities.array_util import generate_label_outlines

def flair_and_ce(flair_file,ce_file,flair_area=20,save=True,outpath=None,FAC=True,FMC=True,ignore_split=False):
    '''
    flair area expected in units of mm, flair and ce file expected to be in the same resolution space and contain mm size slides
    '''
    flair_roi = nib.load(flair_file)
    ce_roi = nib.load(ce_file)

    flair_numpy = flair_roi.get_data()
    ce_numpy = ce_roi.get_data()
    
    if ignore_split:
        ce_numpy[np.nonzero(ce_numpy)] = 1
    rois = np.sort(np.unique(ce_numpy))[1:]

    coronnal_slice_thickness=flair_roi.header['dim'][4]
    sagittal_slice_thickness=flair_roi.header['dim'][5]
    axial_slice_thickness=flair_roi.header['dim'][6]
    
    if outpath is None:
        outpath = ce_file[:ce_file.find('.')]

    for roi in rois:
        ce_numpy_copy = np.copy(ce_numpy)
        ce_numpy_copy[ce_numpy_copy!=roi] = 0
        ce_numpy_copy[ce_numpy_copy==roi] = 1
        flair_numpy_copy = np.copy(flair_numpy)
        flair_numpy_copy[flair_numpy_copy!=0] = 1

        area_of_interest = generate_label_outlines(ce_numpy_copy)
        # area_of_interest = ce_numpy_copy

        x0,y0,z0 = area_of_interest.nonzero()

        if roi == 1:
            area_of_interest=np.zeros(ce_roi.shape)
        else:
            radiusx = math.ceil(flair_area / coronnal_slice_thickness) # radius is used loosely here, there may be images where it is not equal distance per slide in every direction
            radiusy = math.ceil(flair_area / sagittal_slice_thickness)
            radiusz = math.ceil(flair_area / axial_slice_thickness)
            # might be a more efficient/faster way, i.e mask function using a pre-allocated sphere
            for i in range(len(x0)):

                for x in range(x0[i]-radiusx, x0[i]+radiusx+1):
                    for y in range(y0[i]-radiusy, y0[i]+radiusy+1):
                        for z in range(z0[i]-radiusz, z0[i]+radiusz+1):
                            ''' deb: measures how far a coordinate in A is far from the center. 
                                    deb>=0: inside the sphere.
                                    deb<0: outside the sphere.'''   
                            deb = flair_area - math.sqrt((coronnal_slice_thickness*(x0[i]-x))**2 + (sagittal_slice_thickness*(y0[i]-y))**2 + (axial_slice_thickness*(z0[i]-z))**2)
                            if (deb)>=0: area_of_interest[x,y,z] = 1
            area_of_interest = 1 - area_of_interest

        flair_numpy_copy = np.ma.masked_array(flair_numpy_copy,area_of_interest,fill_value=0).filled()
        
        FMC_numpy = np.ma.masked_array(flair_numpy_copy,ce_numpy_copy,fill_value=0).filled()
        FAC_numpy = np.ma.masked_array(flair_numpy_copy,ce_numpy_copy,fill_value=1).filled()

        out_nib = []
        if FAC:
            FAC_nib = nib.Nifti1Image(FAC_numpy,flair_roi.affine,header=flair_roi.header)
            if save:
                nib.save(FAC_nib,outpath+'_FAC.nii.gz')
            else:
                out_nib.append(FAC_nib)
            
        
        if FMC:
            FMC_nib = nib.Nifti1Image(FMC_numpy,flair_roi.affine,header=flair_roi.header)
            if save:
                nib.save(FMC_nib,outpath+'_FMC.nii.gz')
            else:
                out_nib.append(FAC_nib)

        if not save:
            return out_nib


if __name__ == "__main__":
    from joblib import Parallel, delayed
    import multiprocessing
    num_cores = multiprocessing.cpu_count()
    patient_roi_dict = {}
    print('main block')
    for roi in glob('/qtim/users/jcardo/FMS/coreg/*MPRAGE_POST_r_T2_AUTO-label_EG_ROI*'):
        patient=roi[29:35]
        visit=roi[36:44]
        tumor=roi[-10:-7]
        if glob('/qtim2/users/data/FMS/ANALYSIS/ROIs_Finalized/{0}/{1}/*FLAIR*XM*'.format(patient,visit)) is not None:
            patient_roi_dict[patient+'_'+visit+'_'+tumor] = glob('/qtim2/users/data/FMS/ANALYSIS/ROIs_Finalized/{0}/{1}/*FLAIR*XM*'.format(patient,visit))
        elif glob('/qtim2/users/data/FMS/ANALYSIS/ROIs_Finalized/{0}/{1}/*FLAIR*EG*'.format(patient,visit)) is not None:
            patient_roi_dict[patient+'_'+visit+'_'+tumor] = glob('/qtim2/users/data/FMS/ANALYSIS/ROIs_Finalized/{0}/{1}/*FLAIR*EG*'.format(patient,visit))
        
        patient_roi_dict[patient+'_'+visit+'_'+tumor] += [roi]
            
    Parallel(n_jobs=num_cores-2)(delayed(flair_and_ce)(patient_roi_dict[i][0],patient_roi_dict[i][1],FMC=False) for i in patient_roi_dict)
    
