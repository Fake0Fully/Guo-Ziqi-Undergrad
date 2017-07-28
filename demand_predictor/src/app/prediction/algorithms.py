import numpy as np
import pandas as pd
import time
import copy

def warn(*args, **kwargs):
	pass
import warnings
warnings.warn = warn

def get_accuracy(y_true, y_pred):
    from sklearn.metrics import mean_squared_error
    import math
    listing = []
    for x in range(0,len(y_true)):
        listing.append(np.abs((y_true[x] - y_pred[x]) / y_true[x]) * 100)
    mape = np.mean(listing)
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    return mape,rmse

def feature_engineer(df,start,n):
	print('Constructing features for linear regression...')
	df = df.fillna(1.0)
	keys = [c for c in df if c.startswith('2')]
	df=pd.melt(df, id_vars='time', value_vars=keys, value_name='actual')
	##########year,qindex,quarter##########check one by one
	df.ix[0,'year']=1
	df.ix[0,'qindex']=1
	df.ix[0,'quarter'] = df.ix[0,'variable'][5]
	for i in range(1,len(df)):
		df.ix[i,'quarter'] = df.ix[i,'variable'][5]
		if df.ix[i,'variable'][1:4] ==  df.ix[i-1,'variable'][1:4]:
			df.ix[i,'year']=df.ix[i-1,'year']
			if df.ix[i,'variable'][5:6] ==  df.ix[i-1,'variable'][5:6]:
				df.ix[i,'qindex']=df.ix[i-1,'qindex']
			else: 
				df.ix[i,'qindex']=df.ix[i-1,'qindex']+1
		else:
			df.ix[i,'year']=df.ix[i-1,'year']+1
			df.ix[i,'qindex']=df.ix[i-1,'qindex']+1
	##########year,quarter indicator##########
	qlist=[]
	ylist=[]
	for i in range(len(df)):
		qlist.append('q'+ df.ix[i,'variable'][5])
		ylist.append('y'+ df.ix[i,'variable'][:4])
	qlist = pd.DataFrame(pd.get_dummies(qlist)).multiply(df["qindex"], axis="index")
	ylist = pd.DataFrame(pd.get_dummies(ylist)).multiply(df["year"], axis="index")
	df= pd.concat([df, qlist,ylist],axis=1)
	##########last quarter,last week, before last quarter, last quarter last week##########		
	for i in range(len(df)):
		week = df.ix[i,'time']
		quarter = df.ix[i,'qindex']
		if quarter == min(df['qindex']):
			df.ix[i,'abs.time'] = df.ix[i,'time']
		if df.ix[i,'time'] != -26:
			# lastw = np.where((df['time']== week-1) & (df['qindex']== quarter))[0][0] 
			lastw = i - 1
			df.ix[i,'lastw'] = df.ix[lastw,'actual']
			if df.ix[i,'qindex'] > min(df['qindex']):
				lastq = np.where((df['time']== week) & (df['qindex']== quarter-1))[0][0] 
				df.ix[i,'abs.time'] = df.ix[lastq,'abs.time']+13
				df.ix[i,'lastq'] = df.ix[lastq,'actual']
				df.ix[i,'lolastweek'] = df.ix[lastq,'lastw']
				if df.ix[i,'qindex'] > (min(df['qindex'])+ 1):
					beforelastq = np.where((df['time']== week) & (df['qindex']== quarter-2))[0][0] 
					df.ix[i,'before.lastq'] = df.ix[beforelastq,'actual']
	#########modification##########
	df.year = df.year.astype(int)
	df['qindex'] = df['qindex'].astype(int)
	del df['variable'],df['q4']
	df = df.dropna() 
	df['abs.time'] = df['abs.time'].astype(int)

	cols = list(df)
	cols[1], cols[0] = cols[0], cols[1]
	df = df.ix[:,cols]
	#########n average########
	df= df.reset_index(drop=True)

	df['avepnw']=0
	df['avepnl']=0
	df['prop'] = 0
	for i in range(len(df)):
		if (26+df.ix[i,'time']) > n-1:
			df.ix[i,'avepnw'] = df.ix[(i-n+1):i,'lastw'].mean(axis=0) 
			df.ix[i,'avepnl'] = df.ix[(i-n+1):i,'lolastweek'].mean(axis=0)
		else:
			nweek = range((i-(26+df.ix[i,'time'])+1),i+1)
			df.ix[i,'avepnw'] = df.ix[nweek,'lastw'].mean(axis=0)
			df.ix[i,'avepnl'] = df.ix[nweek,'lolastweek'].mean(axis=0)
		df.ix[i,'prop'] = df.ix[i,'avepnw']/df.ix[i,'avepnl']*df.ix[i,'lastq']


	#######train label#######
	#set m as the starting week of testing data 
	df['train'] = 1
	df.loc[(df['qindex'] == (max(df['qindex'])-1))& (df['time']>= (start+13-26)), 'train'] =0
	df.loc[(df['qindex'] == max(df['qindex']))& (df['time']>= start-26), 'train' ] =0
	df.loc[(df['qindex'] == (max(df['qindex'])-2))& (df['time']>= start), 'train'] =2
	df.loc[(df['qindex'] == (max(df['qindex'])-1))& (df['time']>0), 'train' ] =2
	df.loc[(df['qindex'] == max(df['qindex']))& (df['time']>0), 'train' ] =2
	# df.to_csv('feature2.csv')
	
	return df 

def build_regression(dat, start, n):
	print('Building linear regression...')
	from sklearn import datasets, linear_model
	from sklearn.linear_model import ElasticNetCV
	from sklearn.metrics import r2_score
	from sklearn.metrics import mean_absolute_error

	dat = dat.drop(dat.columns[1:-5], axis=1)
	df = feature_engineer(dat,start,n)
	# # Split the targets into training/testing sets
	train = df[df['train']==1]
	test = df[df['train']==0]
	df_x_train = train.ix[:,1:-1] 
	df_x_test = test.ix[:,1:-1] 
	df_y_train = train.ix[:,0] 
	df_y_test = test.ix[:,0] 

	##### The parameter l1_ratio corresponds to alpha in the glmnet R package
	# while alpha corresponds to the lambda parameter in glmnet. Specifically, 
	# l1_ratio = 1 is the lasso penalty. Currently, l1_ratio <= 0.01 is not reliable, 
	# unless you supply your own sequence of alpha.

	df_x_test= df_x_test.reset_index(drop=True)
	lenn = df_x_test[df_x_test['qindex']==max(df_x_test['qindex'])-1].shape[0]
	lena = df_x_test[df_x_test['qindex']==max(df_x_test['qindex'])].shape[0]
	############### elasticnet cv ##########
	temp=[]
	enetcv = ElasticNetCV(l1_ratio=[.01, .1, .2, .3, .4, .5, .6, .7, .8, .9, .95, .99, 1])
	enetcv.fit(df_x_train, df_y_train)

	########## next quarter ###########
	pred_next=[]
	for i in range(lenn):
		y_pre = enetcv.predict(df_x_test.iloc[i,:].values.reshape(1,-1))[0] 
		pred_next.append(y_pre)
		if i < lenn:
			week = df_x_test.ix[i,'time']
			quarter = df_x_test.ix[i,'qindex']
			nextq = np.where((df_x_test['time']==week) & (df_x_test['qindex']==quarter+1))[0][0]
			df_x_test.ix[nextq,'lastq'] = y_pre
			df_x_test.ix[nextq,'avepnl'] = df_x_test.ix[(nextq-n+1):nextq,'lolastweek'].mean(axis=0)
			df_x_test.ix[nextq,'prop'] = df_x_test.ix[nextq,'avepnw']/df_x_test.ix[nextq,'avepnl']*df_x_test.ix[nextq,'lastq']
			if i < lenn-1:
				nextw = np.where((df_x_test['time']==week+1) & (df_x_test['qindex']==quarter))[0][0]
				nextwq = np.where((df_x_test['time']==week+1) & (df_x_test['qindex']==quarter+1))[0][0]
				df_x_test.ix[nextw,'lastw'] = y_pre
				df_x_test.ix[nextwq,'lolastweek'] = y_pre
				df_x_test.ix[nextw,'avepnw'] = df_x_test.ix[max(nextw-n+1,1):nextw,'lastw'].mean(axis=0)
				df_x_test.ix[nextw,'prop'] = df_x_test.ix[nextw,'avepnw']/df_x_test.ix[nextw,'avepnl']*df_x_test.ix[nextw,'lastq']

	############ quarter after next ##########
	pred_afternext = []

	for i in range(lena):
		y_pre = enetcv.predict(df_x_test.iloc[(i+lenn),:].values.reshape(1,-1))[0]
		pred_afternext.append(y_pre)
		if i < lena-1:  
			week = df_x_test.ix[i+lenn,'time']
			quarter = df_x_test.ix[i+lenn,'qindex']
			nextw = np.where((df_x_test['time']==week+1) & (df_x_test['qindex']==quarter))[0][0]
			df_x_test.ix[nextw,'lastw'] = y_pre
			df_x_test.ix[nextw,'avepnw'] = df_x_test.ix[max(nextw-n+1,1):nextw,'lastw'].mean(axis=0)
			df_x_test.ix[nextw, 'prop'] = df_x_test.ix[nextw,'avepnw']/df_x_test.ix[nextw,'avepnl']*df_x_test.ix[nextw,'lastq']
	y_pred_enetcv = pred_next + pred_afternext
	#print(mean_absolute_error(df_y_test, y_pred_enetcv, sample_weight=None, multioutput='uniform_average'))
	r2_score_enetcv = r2_score(df_y_test, y_pred_enetcv)
	# print("r^2 on test data : %f" % r2_score_enetcv)


	return np.array(pred_next), np.array(pred_afternext)

def smooth(dat):
	bestErr = np.inf
	bestParam = (0,0)
	act = copy.deepcopy(dat)
	for alpha in np.arange(0.1,1,0.1):
		for gamma in np.arange(0.1,1,0.1):
			S = act[0]
			B = act[1] - act[0]
			pred = np.array([S])
			for j in range(1, len(act)):
				Snew = alpha * act[j] + (1-alpha) * (S+B)
				Bnew = gamma * (Snew-S) + (1-gamma) * B
				pred = np.append(pred, Snew)
				S = Snew
				B = Bnew
			err = np.sqrt(np.mean((pred[:-1] - act[1:])**2))
			if err < bestErr:
				bestParam = (alpha, gamma)
				bestErr = err
				bestPred = pred[-1]
	return int(bestPred)

def build_vertical(dat,start,reference=None):
	print('Building vertical extrapolation model...')
	start = start - 1
	ncol = dat.shape[1]
	nrow = dat.shape[0]
	scol = 1
	dat_n = dat.iloc[(13+start):26,scol:(ncol-2)]
	nweek = dat_n.shape[0]
	horizon = dat_n.iloc[0].shape[0]
	next_pred = np.array([])
	dat_an = copy.deepcopy(dat)
	if reference is None:
		for i in range(nweek):
			next_pred = np.append(next_pred, smooth(dat_n.iloc[i]))
		return next_pred
	else:
		dat_an.iloc[(13+start):26,ncol-2] = reference
		dat_an = dat_an.iloc[start:26,scol:(ncol-1)]
		nweek = dat_an.shape[0]
		horizon = dat_an.iloc[0].shape[0]
		afternext_pred = np.array([])
		for i in range(nweek):
			afternext_pred = np.append(afternext_pred, smooth(dat_an.iloc[i]))
		return afternext_pred

def build_benchmark(dat, start): # assuming inputs is in list format [[current quarter], [next quarter],[afnext quarter]]
    print('Building proportionate scaling model...')
    pd.options.mode.chained_assignment = None  # default='warn'
    forecast = dat.iloc[:,-3:]
    forecast.iloc[13+start:,1] = None
    forecast.iloc[start:,2] = None
    next_start = max(0,(start+5))
    afternext_start = max(0,(start-8))
    next_ratio = np.mean(forecast.iloc[next_start:start+13, 1]) / np.mean(forecast.iloc[next_start:start+13, 0])
    afternext_ratio = np.mean(forecast.iloc[afternext_start:start, 2]) / np.mean(forecast.iloc[afternext_start:start, 1])
    pred_next = forecast.iloc[start+13:27, 0] * next_ratio
    forecast.iloc[start+13:27, 1] = pred_next
    pred_afternext = forecast.iloc[start:27, 1] * afternext_ratio
    # forecast.iloc[start:27, 2] = pred_afternext
    return np.array(pred_next), np.array(pred_afternext)


# dat = pd.read_csv('./data/consolidated_data_atv.csv',thousands=',')
# dat = pd.read_csv('./data/test_data_atv.csv',thousands=',')
# build_regression(dat,4,5)


