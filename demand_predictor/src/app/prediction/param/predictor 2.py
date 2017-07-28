import algorithms
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from algorithms import *
from 
import sys
import os

def find_start(dat): 
    afternext = dat.iloc[:,-1]
    start = sum(pd.notnull(afternext))
    return start

def get_accuracy(y_true, y_pred):
    from sklearn.metrics import mean_squared_error
    import math
    listing = []
    for x in range(0,len(y_true)):
        listing.append(np.abs((y_true[x] - y_pred[x]) / y_true[x]) * 100)
    mape = np.mean(listing)
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    return mape,rmse

def predict_division(dat, div, start = -1, w1 = None, w2 = None):
    if start < 1:
        start = find_start(dat)
    print div
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

def cross_validation(dat, div, w1=None, w2=None):
    mape = []
    rmse = []
    for i in range(1,14):
        act_next = np.array(dat.iloc[13+i:27,-2])
        act_afternext = np.array(dat.iloc[i:27,-1])
        act = np.append(act_next, act_afternext)
        pred_next, pred_afternext = predict_division(dat, div, start = i, w1 = w1, w2 = w2)
        pred = np.append(pred_next, pred_afternext)
        temp_mape, temp_rmse = get_accuracy(act, pred)
        mape.append(temp_mape)
        rmse.append(temp_rmse)
    ave_mape = sum(mape) / len(mape)
    ave_rmse = sum(rmse) / len(rmse)
    return ave_mape, ave_rmse

def grid_search():
    range_div = ['atv','pmm','ccs','ipc']
    f = open("log.csv", 'w')
    f.write("div, w_reg, w_ver, w_ben, mape, rmse\n")
    total = len(range_div) * 55
    count = 0

    for div in range_div:
        dat = pd.read_csv('./data/consolidated_data_'+div+'.csv', thousands=',')
        for w_reg in range(0,11,1):
            ww_reg = w_reg / 10.0
            for w_ver in range(0,11-w_reg,1):
                ww_ver = w_ver / 10.0
                ww_ben = 1 - ww_reg - ww_ver
                count += 1
                print("====== ", round(count/float(total)*100,2),"% =====")
                a,b = cross_validation(dat, div, w2=[ww_reg, ww_ver, ww_ben])
                content = "" + div + ", " + str(ww_reg) + ", " + str(ww_ver) + ", " + str(ww_ben) + ", " + str(a) + ", " + str(b) + "\n"
                f.write(content)
                f.flush()
    f.close()

def get_quarter():
    import datetime
    month = datetime.datetime.now().month
    if month in [1,2,3]:
        return 'Q1','Q2','Q3','Q4'
    elif month in [4,5,6]:
        return 'Q2','Q3','Q4','Q1'
    elif month in [7,8,9]:
        return 'Q3','Q4','Q1','Q2'
    else:
        return 'Q4','Q1','Q2','Q3'

print get_quarter()


def plot_prediction(datt, pred_next, pred_afternext, div='atv', level=99, start=-1, title='Customer demand (potential) development pieces - OOH (CRD/WT) & sales revenue'):
    _file = os.path.abspath(sys.argv[0])
    PATH = os.path.dirname(_file)
    conf_path_n = PATH + "\\prediction\\param\\" + div + "_next.csv"
    conf_path_an = PATH + "\\prediction\\param\\" + div + "_afternext.csv"
    # conf_path_n = './param/' + div + '_next.csv'
    # conf_path_an = './param/' + div + '_afternext.csv'
    cint_n = pd.DataFrame(pd.read_csv(conf_path_n, thousands=',')).loc[:,'me'+str(level)]
    cint_an = pd.DataFrame(pd.read_csv(conf_path_an, thousands=',')).loc[:,'me'+str(level)]
    cint_n = np.append(0, cint_n)
    cint_an = np.append(0, cint_an)
    x = range(-26, 15)
    if start==-1:
        start = find_start(datt)
    import matplotlib.pyplot as plt
    pred_next = np.append(datt.iloc[12+start,-2], pred_next)
    pred_next_upp = pred_next + 3*cint_n[:pred_next.shape[0]]
    pred_next_low = pred_next - 3*cint_n[:pred_next.shape[0]]
    pred_afternext = np.append(datt.iloc[start-1,-1], pred_afternext)
    pred_afternext_upp = pred_afternext + 3*cint_an[:pred_afternext.shape[0]]
    pred_afternext_low = pred_afternext - 3*cint_an[:pred_afternext.shape[0]]
    fig = plt.figure(figsize=(15,8))
    plt.title(title,position=(0.5,1.07),fontsize=16)
    plt.xlabel('Week in\nQuarter',ha='left')
    plt.ylabel('Quarterly\nOoH/Billings',rotation='horizontal',ha='left')
    plt.plot(x[:datt.iloc[:,-4].dropna().shape[0]], datt.iloc[:,-4].dropna(), '#FF41FF', label='OOHUM_WT_CU_lastQ_pcs', linewidth=2.0)
    plt.plot(x[:datt.iloc[:,-3].dropna().shape[0]], datt.iloc[:,-3].dropna(), '#0085CC', label='OOHUM_WT_CU_actQ_pcs', linewidth=2.0)
    plt.plot(x[:datt.iloc[:,-2].dropna().shape[0]], datt.iloc[:,-2].dropna(), '#74FB42', label='OOHUM_WT_CU_nextQ_pcs', linewidth=2.0)
    plt.plot(x[:datt.iloc[:,-1].dropna().shape[0]], datt.iloc[:,-1].dropna(), '#00FEFF', label='OOHUM_WT_CU_afternextQ_pcs', linewidth=2.0)
    plt.plot(x[12+start:27], pred_next, color='#74FB42', linestyle='--', label='OOHUM_WT_CU_nextQ_pcs (predicted)', linewidth=2.0)
    plt.fill_between(x[12+start:27], pred_next_upp, pred_next_low, facecolor='#74FB42', alpha=0.2, linewidth=0)
    plt.plot(x[start-1:27], pred_afternext, color='#00FEFF', linestyle='--', label='OOHUM_WT_CU_afternextQ_pcs (predicted)', linewidth=2.0)
    plt.fill_between(x[start-1:27], pred_afternext_upp, pred_afternext_low, facecolor='#00FEFF', alpha=0.2, linewidth=0)
    # plt.legend(loc='upper center',bbox_to_anchor=(0.5,0.0),ncol=4,fontsize=10)
    axes=plt.gca()
    axes.set_xlim([-26,14])
    box = axes.get_position()
    axes.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=10)
    xticks=[i for i in x]
    plt.xticks(xticks)
    plt.axvline(x=0,color='k')
    axes.grid(color='k',linestyle='-',alpha=0.1)
    axes.xaxis.set_label_coords(0.99, -0.04)
    axes.yaxis.set_label_coords(-0.05,1.04)
    plt.gcf().text(0.56, 0.2, 'Week 0 = Start of quarter week',fontsize=10)
    quarters = get_quarter()
    plt.gcf().text(0.5,0.5,quarters[0],fontsize=14,color='#FF41FF',fontweight='bold')
    plt.gcf().text(0.75,0.8,quarters[1],fontsize=14,color='#0085CC',fontweight='bold')
    plt.gcf().text(0.33,0.8,quarters[2],fontsize=14,color='#74FB42',fontweight='bold')
    plt.gcf().text(0.17,0.5,quarters[3],fontsize=14,color='#00FEFF',fontweight='bold')
    return fig


# dat = pd.read_csv('./data/test_data_atv.csv', thousands=',')
# i = 4
# a,b = predict_division(dat, 'atv')
# # a,b = build_vertical(dat, i)
# # pred = np.append(a, b)
# # act_next = np.array(dat.iloc[13+i:27,-2])
# # act_afternext = np.array(dat.iloc[i:27,-1])
# # act = np.append(act_next, act_afternext)
# # print get_accuracy(act, pred)
# plot_prediction(dat, a, b, 'atv', 90)
# plt.show()



