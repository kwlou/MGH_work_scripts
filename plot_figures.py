import numpy as np 
import pandas as pd 
from functools import reduce
import seaborn as sns
from math import ceil
from matplotlib import pyplot as plt
import matplotlib.lines as mlines



# automate the registration process with functions

def plot_figures(file_path,title=None,same_cols=True,subplots=None,x_axis=None,y_axis=None,multi_subplots=None,big_plot=None,group2=None,columns=None):
    '''
    Expects Excelfile for a filepath, with different scans as sheets
    same_cols = boolean for if the user wants the same data across all scans (i.e do they all have mean, median)
    subplots = what scans do the user want plotted
    x_axis = what is plotted on the x axis, i.e visits
    y_axis = what is plotted on the y axis, can take in a list, i.e median (to do, functionality for multiple y axis data)
    multi_subplots = do you want multiple figures?
    big_plot = expanding the last plot so there's on dangling subplot for odd numbers, i.e 9 plots leaving 2 by 5 with the last plot empty
    group2 = what are you interested in grouping together to be plotted, i.e patients, tumors, [patients, tumors]
    add different plot type functionality
    '''
    excel = pd.ExcelFile(file_path)
    # excel = pd.ExcelFile('/home/kwlou/Data/HV_ROI_data.xlsx')
    df = {}
    for sheet in excel.sheet_names:
        df[sheet.upper()] = pd.read_excel(excel,sheet)
        df[sheet.upper()].columns = [c.lower() for c in df[sheet.upper()].columns]

    if subplots is None and len(excel.sheet_names) > 1:
        subplots = input("What are you interesting in plotting from {0}? Type all for all, otherwise comma deliminate ".format(df.keys()))

    if subplots.lower() == 'all':
        subplots = [sh.upper() for sh in excel.sheet_names]
    else:
        subplots = subplots.split(',')
        subplots = [sh.upper().strip() for sh in excel.sheet_names]

    # assumes same columns needed for all plots, may not be true, include clause in the multifig creation to choose column infos
    # dont forget the possibility youd want two+ y axis on the same single plot
    col = [set(df[sheet].columns) for sheet in df]
    col = reduce(lambda a,b: a.intersection(b),col)

    if x_axis is None: # cant think of a reason why you'd want plot with different x axis, what are you comparing then? anyways if that comes up, add a same_cols equivalent here
        x_axis = input("What do you want on the x-axis from {0} (expecting 1)? ".format(col))

    if y_axis is None and same_cols:
        y_axis = input("What do you want on the y-axis from {0}? ".format(col))
    y_axis = y_axis.split(',')
    y_axis = [i.lower().strip() for i in y_axis]

    if group2 is None:
        group2 = input("How do you want to group your samples from {0}? ".format(col))
    group2 = group2.split(',')
    group2 = [i.lower().strip() for i in group2]
    if subplots is None and len(excel.sheet_names)==1:
        subplots=group2

    if multi_subplots is None:
        multi_subplots = input("Do you want the data to be plotted as subplots instead of multiple figures (y/n)? ").lower()

    # make the big background plot
    fig, ax = plt.subplots(figsize=(11,11),dpi=300) # this makes the figure and fig.add
    colors = sns.color_palette('colorblind')    
    markers = ['.','o','v','s','x','d']   

    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')
    ax.set_xticks([]) 
    ax.set_yticks([]) 


    if multi_subplots in ['y', 'yes', True, 'True', 'true']:

        ax = fig.add_subplot(1,1,1)
        ax.set_title('Placeholder')
        ax.set_xlabel('Patient Visit # (sample size n= )',fontsize=20)

        if columns is None:
            columns = 2
        rows = ceil(len(subplots)/columns)
        remainder = len(subplots)%columns
        if remainder == 1:
            big_plot = input("What figure(s) would you like expanded on the bottom from {0}, please choose {1}, if any: ".format(df.keys(),remainder)).lower()
            big_plot = big_plot.split(',')
            # no input produces '', i.e if big_plot is in ['', none]

        axs={}
        for i in range(1,len(subplots)+1):
            if big_plot is not None and i == len(subplots):
                axs[i]=fig.add_subplot(rows,1,i) # TO DO - functionality for plots with say [ plot 1 ], [ plot 2 ], [ empty plot ]
            else:
                axs[i]=fig.add_subplot(rows,columns,i)

            # need a clause to deal with subplots being = to sheet
            tmp_df = df[subplots[i-1]].groupby(group2)
            axs[i].plot(tmp_df[x_axis],
                        tmp_df[y_axis] # enter scaling or what have you here
                        )
            #not done

    else:
        ax = fig.add_subplot(1,1,1)
        if title is None:
            ax.set_title('{0}'.format(file_path)) #TODO use combination of find and split to automate title generation
        else:
            ax.set_title(title)
        i=0
        legend_handle_holder=[]
        for sheet in df:
            sheet_color=colors[i]
            grouped_samples = df[sheet].groupby(group2)
            j=0
            for sample in grouped_samples:
                marker=markers[j]
                for y in y_axis:
                    #need some way of distinguishing between multiple y's, might need to use markers and have samples all be the same
                    ax.plot(sample[1][x_axis],sample[1][y],color=sheet_color,marker=marker)
                legend_handle_holder.append(mlines.Line2D([],[],color=sheet_color,marker=marker,label=sample[0] + ' ' + sheet))
                j+=1
            i+=1
        
        plt.legend(handles=legend_handle_holder)
    
    sns.set(font_scale=1.35)
    sns.set_style("white")
    sns.despine( offset=5, trim=False)
        
    plt.savefig('/Users/jv543/{0}.png'.format(title), format='png', dpi=300,bbox_inches='tight')
    plt.close(fig)