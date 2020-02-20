# Parser helper function
from glob import glob
import os
from subprocess import call
from fnmatch import fnmatch

#TODO add list functionality to this
def files_to_list(basedir,files_of_interest,except_case=None):
    '''
    expects a basedir and files_of_interest as strings, returns generator object containing the directory of the files of interest
    '''
    for root, dirs, files in os.walk(basedir):
        for name in files:
            if except_case is not None:
                if fnmatch(name,files_of_interest) and not any([fnmatch(i,except_case) for i in files]):
                    yield os.path.join(root, name)
            else:
                if fnmatch(name,files_of_interest):
                    yield os.path.join(root, name)

