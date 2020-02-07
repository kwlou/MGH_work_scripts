# Parser helper function
from glob import glob
import os
from subprocess import call
from fnmatch import fnmatch


def files_to_list(basedir,files_of_interest):
    '''
    expects a basedir and files_of_interest as strings, returns generator object containing the directory of the files of interest
    '''
    for root, dirs, files in os.walk(basedir):
        for name in files:
            if fnmatch(name,files_of_interest):
                yield os.path.join(root, name)
