import os
import numpy as np
import pandas as pd
import SimpleITK as sitk
import six
import sys
from radiomics import imageoperations, featureextractor

def radiomic_feature_extraction(casename,image_path,roi_path,save_dir,param_file='/home/kwl16/Projects/kwlqtim/mets_Params.yml'):
	params = param_file #replace with location of parameters file
	extractor = featureextractor.RadiomicsFeatureExtractor(params)

	#specify the image and roi path names and which case
	casename = casename
	image_path = image_path #replace with location of image file
	roi_path = roi_path #replace with location of roi file

	#load image and roi
	image = sitk.ReadImage(image_path)
	roi = sitk.ReadImage(roi_path)

	#check for presence of labels (1,2,3) in roi
	roi_arr = sitk.GetArrayFromImage(roi) #image -> array
	met_labels = np.unique(roi_arr)[1:] #which labels are present in the roi?

	radiomics_table = None

	for i, label in enumerate(met_labels):
		if len(np.where(roi_arr==label)[0]) <= 10: # remove tumors smaller than 10 voxels
			continue
		if len(np.unique(np.where(roi_arr==label)[0])) == 1 or len(np.unique(np.where(roi_arr==label)[1])) == 1 or len(np.unique(np.where(roi_arr==label)[2])) == 1: # drop 1-d, or 2-d ROIs
			continue
		label_mask = np.where(roi_arr == label) #identify where the label is in the original roi
		single_label_roi_arr = np.zeros(roi_arr.shape) #create a dummy roi
		single_label_roi_arr[label_mask] = 1 #assign a label of 1 in the dummy roi where the label was in the original roi
		single_label_roi = sitk.GetImageFromArray(single_label_roi_arr) #array -> image
		single_label_roi.CopyInformation(image)
		
		#extract features
		result = extractor.execute(image,single_label_roi)
		
		#put features in a table
		if radiomics_table is None:
			radiomics_table = pd.DataFrame(index=list(result.keys()) , columns = [label]).T
		radiomics_table.loc[label]=list(result.values())
		
	save_path = save_dir #replace with location for file to be saved

	#save feature table
	radiomics_table.to_csv(os.path.join(save_path,casename + '-radiomics.csv'))