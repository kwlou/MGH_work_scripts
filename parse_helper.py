# Parser helper function
from glob import glob
import os
from subprocess import call
from fnmatch import fnmatch
from datetime import datetime, date

#TODO add list functionality to this
def files_to_list(basedir,files_of_interest,subdir='',except_case=None):
    '''
    expects a basedir and files_of_interest as strings or list of strings 
    returns generator object containing the directory of the files of interest

    optional input for subdirectory found within basedir - separated by some other directories
    '''
    if type(files_of_interest) == str:
        files_of_interest = [files_of_interest]
    for root, dirs, files in os.walk(basedir):
        for name in files:
            for file_string in files_of_interest:
                if except_case is not None:
                    if fnmatch(name,file_string) and subdir in root.split(basedir)[1] and not any([fnmatch(i,except_case) for i in files]):
                        yield os.path.join(root, name)
                else:
                    if fnmatch(name,file_string) and subdir in root.split(basedir)[1]:
                        yield os.path.join(root, name)

def folders_to_list(basedir,files_of_interest,except_case=None):
    '''
    expects a basedir and files_of_interest as strings, returns generator object containing the directory of the files of interest
    '''
    if type(files_of_interest) == str:
        files_of_interest = [files_of_interest]
    for root, dirs, files in os.walk(basedir):
        for name in dirs:
            for file_string in files_of_interest:
                if except_case is not None:
                    if fnmatch(name,file_string) and not any([fnmatch(i,except_case) for i in files]):
                        yield os.path.join(root, name)
                else:
                    if fnmatch(name,file_string):
                        yield os.path.join(root, name)

def files_by_date(filelist):
    return sorted(filelist,key=os.path.getctime)

def find_associated_roi(file_path,roi_dir):
    """
    finds the roi associated with the input file_path
    assumes it shares the qtim file nomenclature with patient, visit, and file name delimited by -
    """
    patient = os.path.basename(file_path).split('-')[0]
    visit = os.path.basename(file_path).split('-')[1]
    roi = list(files_to_list(roi_dir, patient+'*'+visit+'*label_*'))
    if not roi:
        print('no roi for ' + file_path)
        return
    return roi[0]
