import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from algorithms import *
from utils import *
import sys
import os

def predict_division(dat, div, start = -1, w1 = None, w2 = None):
    if start < 1:
        start = find_start(dat)
    if div.lower() == 'atv':
        weights1 = [0.6, 0.4, 0.0] if w1 == None else w1
        weights2 = [0.4, 0.6, 0.0] if w2 == None else w2
        next_regression, afternext_regression = build_regression(dat, start, 2)
        next_vertical = build_vertical(dat, start)
        next_benchmark, afternext_benchmark = build_benchmark(dat, start)
        pred_next = weights1[0] * next_regression + weights1[1] * next_vertical + weights1[2] * next_benchmark
        afternext_vertical = build_vertical(dat, start, pred_next)
        pred_afternext = weights2[0] * afternext_regression + weights2[1] * afternext_vertical + weights2[2] * afternext_benchmark

    elif div.lower() == 'pmm':
        weights1 = [0.6, 0.1, 0.3] if w1 == None else w1
        weights2 = [0.0, 1.0, 0.0] if w2 == None else w2
        next_regression, afternext_regression = build_regression(dat, start, 6)
        next_vertical = build_vertical(dat, start)
        next_benchmark, afternext_benchmark = build_benchmark(dat, start)
        pred_next = weights1[0] * next_regression + weights1[1] * next_vertical + weights1[2] * next_benchmark
        afternext_vertical = build_vertical(dat, start, pred_next)
        pred_afternext = weights2[0] * afternext_regression + weights2[1] * afternext_vertical + weights2[2] * afternext_benchmark

    elif div.lower() == 'ccs':
        weights1 = [0.0, 1.0, 0.0] if w1 == None else w1
        weights2 = [0.7, 0.3, 0.0] if w2 == None else w2
        next_regression, afternext_regression = build_regression(dat, start, 4)
        next_vertical = build_vertical(dat, start)
        next_benchmark, afternext_benchmark = build_benchmark(dat, start)
        pred_next = weights1[0] * next_regression + weights1[1] * next_vertical + weights1[2] * next_benchmark
        afternext_vertical = build_vertical(dat, start, pred_next)
        pred_afternext = weights2[0] * afternext_regression + weights2[1] * afternext_vertical + weights2[2] * afternext_benchmark

    elif div.lower() == 'ipc':
        weights1 = [0.4, 0.1, 0.5] if w1 == None else w1
        weights2 = [0.5, 0.0, 0.5] if w2 == None else w2
        next_regression, afternext_regression = build_regression(dat, start, 1)
        next_vertical = build_vertical(dat, start)
        next_benchmark, afternext_benchmark = build_benchmark(dat, start)
        pred_next = weights1[0] * next_regression + weights1[1] * next_vertical + weights1[2] * next_benchmark
        afternext_vertical = build_vertical(dat, start, pred_next)
        pred_afternext = weights2[0] * afternext_regression + weights2[1] * afternext_vertical + weights2[2] * afternext_benchmark

    else:
        return '[Error]: Please enter valid capitalized division name.'

    print "prediction completed"
    return pred_next, pred_afternext

def plot_prediction(datt, pred_next, pred_afternext, margin_next, margin_afternext, ratio=1, start=-1, capa1=0, capa2=0, name1="", name2="", title='Customer demand (potential) development pieces - OOH (CRD/WT) & sales revenue'):
    _file = os.path.abspath(sys.argv[0])
    PATH = os.path.dirname(_file)
    PARAM_FILE = PATH[:-8] + "\\parameters.txt"
    params = open(PARAM_FILE, "r")
    keys = params.readlines()
    title_font, label_font, ticks_font, legend_font, quarter_font, capa_font = [int(str(x).strip().split(':')[1].strip(' ')) for x in keys]

    x = range(-26, 15)
    if start==-1:
        start = find_start(datt)
    import matplotlib.pyplot as plt
    import matplotlib
    scale = 1000

    pred_next = np.append(datt.iloc[12+start,-2], pred_next) / scale
    margin_next = margin_next[:pred_next.shape[0]]*ratio / scale
    pred_next_upp = pred_next + margin_next
    pred_next_low = pred_next - margin_next
    pred_afternext = np.append(datt.iloc[start-1,-1], pred_afternext) / scale
    margin_afternext = margin_afternext[:pred_afternext.shape[0]]*ratio / scale
    pred_afternext_upp = pred_afternext + margin_afternext
    pred_afternext_low = pred_afternext - margin_afternext

    fig = plt.figure(figsize=(15,9))
    plt.title(title,position=(0.5,1.0),fontsize=title_font)
    plt.xlabel('Week in\nQuarter',ha='left',fontsize=label_font)
    plt.ylabel('Quarterly\nOoH/Billings (k)',rotation='horizontal',ha='left',fontsize=label_font)
    plt.plot(x[:datt.iloc[:,-1].dropna().shape[0]], datt.iloc[:,-1].dropna()/scale, '#00FEFF', label='OOHUM_WT_CU_afternextQ_pcs', linewidth=2.0)
    plt.plot(x[:datt.iloc[:,-2].dropna().shape[0]], datt.iloc[:,-2].dropna()/scale, '#74FB42', label='OOHUM_WT_CU_nextQ_pcs', linewidth=2.0)
    plt.plot(x[:datt.iloc[:,-3].dropna().shape[0]], datt.iloc[:,-3].dropna()/scale, '#0085CC', label='OOHUM_WT_CU_actQ_pcs', linewidth=2.0)
    plt.plot(x[:datt.iloc[:,-4].dropna().shape[0]], datt.iloc[:,-4].dropna()/scale, '#FF41FF', label='OOHUM_WT_CU_lastQ_pcs', linewidth=2.0)
    
    plt.plot(x[12+start:27], pred_next, color='#74FB42', linestyle='--', label='OOHUM_WT_CU_nextQ_pcs (predicted)', linewidth=2.0)
    plt.fill_between(x[12+start:27], pred_next_upp.astype(float), pred_next_low.astype(float), facecolor='#74FB42', alpha=0.2, linewidth=0.1)
    plt.plot(x[start-1:27], pred_afternext, color='#00FEFF', linestyle='--', label='OOHUM_WT_CU_afternextQ_pcs (predicted)', linewidth=2.0)
    plt.fill_between(x[start-1:27], pred_afternext_upp.astype(float), pred_afternext_low.astype(float), facecolor='#00FEFF', alpha=0.2, linewidth=0.1)

    plt.tick_params(axis='both', which='major', labelsize=ticks_font)
    axes=plt.gca()
    axes.set_xlim([-26,14])
    box = axes.get_position()
    axes.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    axes.margins(y=.1, x=.1)
    axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=legend_font)
    xticks=range(-26, 15, 2)
    plt.xticks(xticks)
    plt.axvline(x=0,color='k')

    if capa1 != 0:
        capa1 = capa1 * 13
        plt.axhline(y=capa1,xmin=0.57,xmax=0.72,color='r',linewidth=2)
    if capa2 != 0:
        capa2 = capa2 * 13
        plt.axhline(y=capa2,xmin=0.57,xmax=0.72,color='r',linewidth=2)
    axes.annotate(name1, (3, capa1), xytext=(0.5, 0), textcoords='offset points', va='center', ha='left', color='r', fontsize=capa_font, fontweight='bold')
    axes.annotate(name2, (3, capa2), xytext=(0.5, 0), textcoords='offset points', va='center', ha='left', color='r', fontsize=capa_font, fontweight='bold')
    axes.grid(color='k',linestyle='-',alpha=0.1)
    axes.xaxis.set_label_coords(0.99, -0.04)
    axes.yaxis.set_label_coords(-0.15,1.02)
    axes.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.gcf().text(0.56, 0.2, 'Week 0 = Start of quarter week',fontsize=label_font)
    quarters = get_quarter()
    axes.annotate(quarters[0],(x[10], np.array(datt.iloc[:,-4].dropna())[10]/scale), xytext=(20, -20), textcoords='offset pixels', fontsize=quarter_font,color='#FF41FF',fontweight='bold')
    axes.annotate(quarters[1],(x[26], np.array(datt.iloc[:,-3].dropna())[-1]/scale), xytext=(20, -20), textcoords='offset pixels', fontsize=quarter_font,color='#0085CC',fontweight='bold')
    axes.annotate(quarters[2],(x[13+start-1], np.array(datt.iloc[:,-2].dropna())[-1]/scale), xytext=(0, 20), textcoords='offset pixels', fontsize=quarter_font,color='#74FB42',fontweight='bold')
    axes.annotate(quarters[3],(x[start-1], np.array(datt.iloc[:,-1].dropna())[-1]/scale), xytext=(0, 20), textcoords='offset pixels', fontsize=quarter_font,color='#00FEFF',fontweight='bold')
    return fig

# _file = os.path.abspath(sys.argv[0])
# PATH = os.path.dirname(_file)
# p = PATH + "\\data\\test_data_atv.csv"
# dat = pd.read_csv(p, thousands=',')
# dat = pd.read_csv('./data/test_data_atv.csv', thousands=',')

# i = 4
# a,b = predict_division(dat, 'atv')
# temp_next = np.append(dat.iloc[:,-2], a.astype(int))
# print temp_next[~np.isnan(temp_next)].mean()
# # a,b = build_vertical(dat, i)
# # pred = np.append(a, b)
# # act_next = np.array(dat.iloc[13+i:27,-2])
# # act_afternext = np.array(dat.iloc[i:27,-1])
# # act = np.append(act_next, act_afternext)
# # print get_accuracy(act, pred)
# plot_prediction(dat, a, b, 'atv', 1000, 2000)
# plt.show()



