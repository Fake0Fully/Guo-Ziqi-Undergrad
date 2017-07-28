import pandas as pd
import numpy as np

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
