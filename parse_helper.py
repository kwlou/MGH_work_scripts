# Parser helper function
from glob import glob
import os
from subprocess import call


basedir = '/qtim2/users/data/BAV/ANALYSIS/COREGISTRATION/'

for root, dirs, files in os.walk(basedir):
   for name in files:
      print(os.path.join(root, name))
   for name in dirs:
      print(os.path.join(root, name))

      #generator type object with __iter__() and __next__() methods