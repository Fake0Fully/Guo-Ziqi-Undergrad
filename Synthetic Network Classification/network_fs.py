import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.utils import shuffle
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier




seed = 7

filename = 'network.csv'
df = pd.read_csv(filename)
df = df.loc[:,'network':'diameter']
df_c = df.iloc[1200:,:]
df = df.iloc[0:1200,:]
df_c = shuffle(df_c,random_state=seed)
df = shuffle(df,random_state=seed)

def get_network(x):
	name = x.split('_')[0]
	return name
df['network'] = df.network.apply(get_network)
df_c['network'] = df_c.network.apply(get_network)

y = df['network']
yc = df_c['network']
X = df.drop('network',1)
Xc = df_c.drop('network',1)
features = X.columns.values

from sklearn.feature_selection import VarianceThreshold,SelectKBest,chi2,RFE

def get_ranking(myList,desc=True):
	order = [i[0] for i in sorted(enumerate(myList), key = lambda x:x[1], reverse=desc)]
	return features[order]

Xnorm = (X - X.mean()) / (X.max() - X.min())
threshold = 0.95
vt = VarianceThreshold().fit(Xnorm)
feat_var_threshold = X.columns[vt.variances_ > threshold*(1-threshold)]
print 'Variance Threshold:'
print feat_var_threshold
print get_ranking(vt.variances_)
print sorted(vt.variances_, reverse=True)

Xmin = (X - X.min()) / (X.max() - X.min())
chi = SelectKBest(score_func = chi2).fit(Xmin,y)
print '\nChi-squared test:'
print get_ranking(chi.scores_)
print sorted(chi.scores_, reverse=True)


rfe = RFE(SVC(kernel='linear',C=10),1)
rfe.fit(Xnorm,y)
print '\nRecursive Feature Elimination:'
print get_ranking(rfe.ranking_,desc=False)

dc = DecisionTreeClassifier()
dc.fit(Xnorm,y)
print '\nDecision Tree Feature Importance (Gini):'
print get_ranking(dc.feature_importances_)
print sorted(dc.feature_importances_, reverse=True)

rf = DecisionTreeClassifier(criterion='entropy')
rf.fit(Xnorm,y)
print '\nDecision Tree Feature Importance (Entropy):'
print get_ranking(rf.feature_importances_)
print sorted(rf.feature_importances_, reverse=True)
