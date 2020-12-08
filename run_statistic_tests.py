import numpy as np 
import pandas as pd 
from functools import reduce
from scipy import stats
from math import ceil

# wilcoxon sign-ed rank test - non-parametric test (no assumed distribution of data), paired data
def run_wilcoxon(excelfile,excelfile2=None,outfile=None,scans=None,compared_stat=None,pairing=None,paired_differentiator=None,baseline_control=None,experimental=None):
    if excelfile2 is None:
        excel = pd.ExcelFile(excelfile)
        
        # #testing
        # excel = pd.ExcelFile('/home/kwlou/Data/FMS_CE_summary_stats.xlsx')
        # #
        df = {}
        for sheet in excel.sheet_names:
            if sheet.upper() not in ['METHODS','METHOD','METHODOLOGY']:
                df[sheet.upper()] = pd.read_excel(excel,sheet)
                df[sheet.upper()] = df[sheet.upper()].replace(np.nan,'',regex=True)
                df[sheet.upper()] = df[sheet.upper()].iloc[:,:14]#12 for non SUV
                #this is because this 13-482 had columns start in iloc3
                # df[sheet.upper()].columns = list(df[sheet.upper()].iloc[1])
                #
                df[sheet.upper()].columns = [c.lower() for c in df[sheet.upper()].columns]
        
        if scans is None:
            scans = input("What scan types are you interested in from {0}? Type all for all, otherwise comma deliminate: ".format(df.keys()))
        
        if scans.lower() == 'all':
            scans = [sh.upper() for sh in df.keys()]
        elif type(scans) is str:
            scans = scans.split(',')
            scans = [sh.upper().strip() for sh in scans]

        # col = [set(df[sheet].columns) for sheet in scans]
        # col = reduce(lambda a,b: a.intersection(b),col)
        col = [df[sheet].columns for sheet in scans]
        col = [i for j in col for i in j]
        col = list(set(col)) # remove duplicates
        
        if compared_stat is None:
            if 'median' in col: # i think this is going to be the most common stat, median voxel between pairs
                compared_stat = ['median']
            else:
                compared_stat = input('What stats are you comparing between your sample pairs from {0}? '.format(col))
        if type(compared_stat)==str:
            compared_stat = compared_stat.split(',')
            compared_stat = [i.lower().strip() for i in compared_stat]
            for i in compared_stat:
                if i not in col:
                    raise KeyError('one or more of your inputs are not in {0}'.format(col))

                
        if pairing is None:
            pairing = input("What is the common variable(s) between pairs, (i.e subject, t#) from {0} ".format(col))
        
        if type(pairing) is str:
            pairing = pairing.split(',')
            pairing = [i.lower().strip() for i in pairing]

        tmp_differentiator = col
        for i in pairing:
            tmp_differentiator.remove(i)
        
        # to do - implement this, currently assumes visit is the differentiator and just does v1 vs v2-to-n
        if paired_differentiator is None:
            paired_differentiator = input("How are you differentiating between your pairs from {0}".format(tmp_differentiator))
             
        wilc_results = {}
        paired_values = {}
        p_diff_values = []
        for scan in scans:
            df_groupby = df[scan].groupby(pairing)
            wilc_results[scan] = {}
            paired_values[scan] = {}
            for feature in compared_stat:
                paired_values[scan][feature]={}
                wilc_results[scan][feature]={}
                if feature in df[scan].columns:
                    for group in df_groupby:
                        for i in range(1,group[1].shape[0]):
                            BL = group[1].iloc[0][feature]  
                            if BL == '':
                                BL = np.nan
                            EXP_VALUE = group[1].iloc[i][feature]
                            # assumes first row of each groupby is the baseline visit (VISIT_01)    
                            if type(BL) == str and '<' in BL:
                                numbers_past_decimal = len(BL[BL.find('0.'):])-2
                                BL = float(BL[BL.find('0.'):]) - float('0.' + '0'*(numbers_past_decimal-1) + '1')
                            if type(EXP_VALUE) == str and '<' in EXP_VALUE:
                                numbers_past_decimal = len(EXP_VALUE[EXP_VALUE.find('0.'):])-2
                                EXP_VALUE = float(EXP_VALUE[EXP_VALUE.find('0.'):]) - float('0.' + '0'*(numbers_past_decimal-1) + '1')
                            elif EXP_VALUE=='':
                                continue
                            if group[1].iloc[i][paired_differentiator] not in paired_values[scan][feature].keys():
                                paired_values[scan][feature][group[1].iloc[i][paired_differentiator]]=[]
                            paired_values[scan][feature][group[1].iloc[i][paired_differentiator]].extend([BL - EXP_VALUE])
                            if group[1].iloc[i][paired_differentiator] not in p_diff_values:
                                p_diff_values.append(group[1].iloc[i][paired_differentiator])
                    for v in paired_values[scan][feature].keys():
                        wilc_results[scan][feature][v] = (stats.wilcoxon(paired_values[scan][feature][v]), len(paired_values[scan][feature][v]))
                        print(scan + ' ' + feature + ' ' + str(v) + ' ' + str(paired_values[scan][feature][v]))
            

    if outfile is None:
        outfile = excelfile[:-5] + '_wilc.txt'
    
    p_diff_values.sort()
    f = open(outfile,"w+")
    for scan in wilc_results:
        f.write(scan + '\n')
        for feature in compared_stat:
            if feature in df[scan].keys():
                f.write(feature + ' '*5)
        f.write('\n')
        for feature in compared_stat:
            if feature in df[scan].keys():        
                f.write("{0} Wilcoxon(W) Sample_size(n) p-value  ".format(paired_differentiator))
        f.write('\n')
        for p_diff in p_diff_values: 
            for feature in compared_stat:
                if feature in df[scan].keys():
                    if p_diff in wilc_results[scan][feature].keys():
                        f.write("{0} {1} {2} {3}  ".format(p_diff,wilc_results[scan][feature][p_diff][0][0],wilc_results[scan][feature][p_diff][1],wilc_results[scan][feature][p_diff][0][1]))
                    else:
                        f.write(" "*5)
            f.write('\n')
        f.write("\n\n\n")

run_wilcoxon('/home/kwl16/Data/FMS_CE_summary_stats.xlsx',outfile='/home/kwl16/Data/wilc_SUVpeak_FMS.txt',scans='SUV',pairing='subj,t#',paired_differentiator='visit',compared_stat='SUVpeak')


# dicme={}
# for group in x2:
#     for i in range(1,group[1].shape[0]):
#         if dicme[group[1].iloc[i]['visit']]
#         dicme[group[1].iloc[i]['visit']].extend([group[1].iloc[0]['plgf'] - group[1].iloc[i]['plgf']])