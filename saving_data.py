import pandas as pd
import xlsxwriter
import numpy as np
import os

def parse_text_to_excel():
    pass

def numpy_to_excel(array,filename,sheets=None,outpath='/home/kwlou/Data/',*args):

    if type(array) is not np.ndarray:
        print('No numpy array detected: exitting')
        return
    if array.ndim == 1:
        array = np.array([array])
    
    df={}
    if array.ndim == 3:
        for i in range(x.shape[0]):
            df[i] = pd.DataFrame(data=array[i::],columns=args)
    elif array.ndim == 2:
        df[0] = pd.DataFrame(data=array,columns=args)
    elif array.ndim > 3:
        print('you have 4d data, come back to saving_data.py and figure out how to organize it')
        return

    writer = pd.ExcelWriter(outpath+filename, engine = 'xlsxwriter')
    if sheets is not None:
        for i in len(df.keys()):
            df[i].to_excel(writer, sheet_name=sheets[i])
    else:
        for i in len(df.keys()):
            df[i].to_excel(writer)

def numpy_to_text():
    pass