import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
import time

from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import KFold,cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import BaggingClassifier, ExtraTreesClassifier, GradientBoostingClassifier, VotingClassifier, RandomForestClassifier, AdaBoostClassifier
from sklearn.grid_search import GridSearchCV

def logloss(act,pred):
    epsilon = 1e-15
    pred = sp.maximum(epsilon,pred)
    pred = sp.minimum(1-epsilon,pred)
    ll = sum(act*sp.log(pred) + sp.subtract(1,act)*sp.log(sp.subtract(1,pred)))
    ll = ll * -1.0/len(act)
    return ll
    
filename = 'data.csv'
raw = pd.read_csv(filename)

loc_x_zero = raw['loc_x'] == 0

raw['remaining_time'] = raw['minutes_remaining'] * 60 + raw['seconds_remaining']

# rare_action_types = raw['action_type'].value_counts().sort_values().index.values[:20]
# raw.loc[raw['action_type'].isin(rare_action_types), 'action_type'] = 'Other'

raw['home_play'] = raw['matchup'].str.contains('vs').astype('int')

raw['seconds_from_period_end'] = 60 * raw['minutes_remaining'] + raw['seconds_remaining']
raw['last_5_sec_in_period'] = (raw['seconds_from_period_end'] < 5).astype('int')

raw.loc[raw['period'].isin([6,7]),'period'] = 5
raw.loc[raw['season'].isin(['2014-15','2015-16','2013-14','2012-13']),'season'] = 'Other'
raw['shot_distance'] = pd.cut(raw['shot_distance'],8)
raw['loc_x'] = pd.cut(raw['loc_x'],25)
raw['loc_y'] = pd.cut(raw['loc_y'],25)

raw['game_date'] = pd.to_datetime(raw['game_date'])
raw['game_year'] = raw['game_date'].dt.year
raw['game_month'] = raw['game_date'].dt.month

drops = ['shot_id', 'team_id', 'team_name', 'shot_zone_area', \
         'matchup', 'lon', 'lat', 'seconds_remaining','seconds_from_period_end', 'minutes_remaining', \
          'game_event_id', 'game_id','game_date']
for drop in drops:
    raw = raw.drop(drop, 1)

categorical_vars = ['action_type','loc_x','loc_y','combined_shot_type','shot_type','game_year','game_month', 'shot_zone_basic','shot_zone_range','shot_distance','opponent', 'period', 'season']
for var in categorical_vars:
    raw = pd.concat([raw, pd.get_dummies(raw[var], prefix=var)], 1)
    raw = raw.drop(var,1)
    
df = raw[pd.notnull(raw['shot_made_flag'])]
submission = raw[pd.isnull(raw['shot_made_flag'])]
submission = submission.drop('shot_made_flag',1)
train_X = df.drop('shot_made_flag',1)
train_y = df['shot_made_flag']

# from sklearn.feature_selection import VarianceThreshold,SelectKBest,chi2,RFE
# threshold = 0.90
# vt = VarianceThreshold().fit(train_X)
# feat_var_threshold = df.columns[vt.variances_ > threshold*(1-threshold)]
# model = RandomForestClassifier()
# model.fit(train_X,train_y)
# feat_imp = pd.DataFrame(model.feature_importances_,index=train_X.columns,columns=['importance'])
# feat_imp_20 = feat_imp.sort_values('importance',ascending=False).head(20).index

# from sklearn.preprocessing import MinMaxScaler
# X_minmax = MinMaxScaler(feature_range=(0,1)).fit_transform(train_X)
# X_scored = SelectKBest(score_func=chi2,k='all').fit(X_minmax,train_y)
# feature_scoring = pd.DataFrame({'feature':train_X.columns,'score':X_scored.scores_})
# feat_scored_20 = feature_scoring.sort_values('score',ascending=False).head(20)['feature'].values

# rfe = RFE(LogisticRegression(),20)
# rfe.fit(train_X,train_y)
# feature_rfe_scoring = pd.DataFrame({
#    'feature':train_X.columns,
#    'score':rfe.ranking_
#    })
# feat_rfe_20 = feature_rfe_scoring[feature_rfe_scoring['score']==1]['feature'].values

# features = np.hstack([
#    feat_imp_20,
#    feat_scored_20,
#    feat_rfe_20
#    ])
# features = np.unique(features)
#print('Final features set:\n')
#for f in features:
#    print('\t-{}'.format(f))

seed = 7
processors = 1
n_folds = 3
n_ins = len(train_X)
scoring = 'log_loss'
kfold = KFold(n=n_ins,shuffn_folds=n_folds,random_state=seed)
#models = []
#models.append(('LR',LogisticRegression()))
#models.append(('LDA',LinearDiscriminantAnalysis()))
#models.append(('KNN',KNeighborsClassifier(n_neighbors=5)))
#models.append(('CART',DecisionTreeClassifier()))
#models.append(('NB',GaussianNB()))
#
#results = []
#names = []
#
#for name,model in models:
#    cv_results = cross_val_score(model,train_X,train_y,cv=kfold,scoring=scoring,n_jobs=processors)
#    results.append(cv_results)
#    names.append(name)
#    print("{0}: ({1:.3f}) +/- ({2:.3f})".format(name, cv_results.mean(), cv_results.std()))


def cv_optimize(clf,parameters,Xtrain,ytrain,n_folds=kfold,score=scoring,jobs=processors):
    gs = GridSearchCV(clf,param_grid=parameters,cv=n_folds,scoring=score,n_jobs=jobs)
    gs.fit(Xtrain,ytrain)
    print 'BEST PARAMS',gs.best_params_
    results = cross_val_score(gs.best_estimator_, train_X, train_y, cv=kfold, scoring=scoring,n_jobs=processors)
    print("({0:.6f}) +/- ({1:.6f})".format(results.mean(), results.std()))
    best = gs.best_estimator_
    return best

lr_grid = cv_optimize(
    LogisticRegression(random_state=seed),
    parameters = {
        'penalty':['l1'],
        'C':[0.55]},
    Xtrain = train_X,ytrain = train_y)
    
# rf_grid = cv_optimize(
#     RandomForestClassifier(warm_start=True,random_state=seed),
#     parameters = {
#         'n_estimators':[200],
#         'criterion':['gini'],
#         'max_features':[20],
#         'max_depth':[10],
#         'bootstrap':[True]},
#     Xtrain = train_X,ytrain = train_y)

# ada_grid = cv_optimize(
#     AdaBoostClassifier(random_state=seed),
#     parameters = {
#         'algorithm':['SAMME','SAMME.R'],
#         'n_estimators':[10,25],
#         'learning_rate':[1e-3,1e-2]},
#     Xtrain = train_X,ytrain = train_y)
    
# gbm_grid = cv_optimize(
#     GradientBoostingClassifier(warm_start=True,random_state=seed),
#     parameters = {
#         'n_estimators':[100],
#         'max_depth':[5,6],
#         'max_features':[20],
#         'learning_rate':[1e-1]},
#     Xtrain = train_X,ytrain = train_y)

# etc_grid = cv_optimize(
#     ExtraTreesClassifier(warm_start=True,random_state=seed),
#     parameters = {
#         'n_estimators':[100,200],
#         'max_depth':[None,10],
#         'max_features':['auto',10,20]
#     },
#     Xtrain = train_X,ytrain = train_y
# )
# estimators = []
# estimators.append(('lr',lr_grid))
# estimators.append(('gbm',gbm_grid))
# estimators.append(('rf',rf_grid))
# estimators.append(('ada',ada_grid))
# estimators.append(('knn',knn_grid))
# ensemble = VotingClassifier(estimators,voting='soft',weights=[1,2,3])
# results = cross_val_score(ensemble, train_X, train_y, cv=kfold, scoring=scoring,n_jobs=processors)
# print("({0:.3f}) +/- ({1:.3f})".format(results.mean(), results.std()))

lr_grid.fit(train_X,train_y)
pred = lr_grid.predict_proba(submission)
sub = pd.read_csv('sample_submission.csv')
sub['shot_made_flag'] = pred[:,1]
sub.to_csv('sub.csv',index=False)