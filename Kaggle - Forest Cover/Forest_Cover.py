
# coding: utf-8

# In[1]:

# get_ipython().magic(u'matplotlib inline')
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import KFold,cross_val_score,StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import BaggingClassifier, ExtraTreesClassifier, GradientBoostingClassifier, VotingClassifier, RandomForestClassifier, AdaBoostClassifier
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import log_loss,accuracy_score,roc_auc_score
import xgboost as xgb


# In[2]:

df = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')
# print df.head()




# print df.dtypes




# print df.isnull().sum()




df.describe()




df.Wilderness_Area1.unique()




df.ix[:,:11].hist(figsize=(16,12),bins=50)
# plt.show()




def r(x):
    if x+180>360:
        return x-180
    else:
        return x+180

df['Aspect2'] = df.Aspect.map(r)
test['Aspect2'] = test.Aspect.map(r)




df['Highwater'] = df.Vertical_Distance_To_Hydrology < 0
test['Highwater'] = test.Vertical_Distance_To_Hydrology < 0

def plotc(c1,c2):

    fig = plt.figure(figsize=(16,8))
    sel = np.array(list(df.Cover_Type.values))

    plt.scatter(c1, c2, c=sel, s=100)
    plt.xlabel(c1.name)
    plt.ylabel(c2.name)
# plotc(df.Elevation-df.Vertical_Distance_To_Hydrology, df.Vertical_Distance_To_Hydrology)


# plotc(df.Elevation-df.Horizontal_Distance_To_Hydrology*0.2, df.Horizontal_Distance_To_Hydrology)


df['Distanse_to_Hydrolody'] = (df['Horizontal_Distance_To_Hydrology']**2+df['Vertical_Distance_To_Hydrology']**2)**0.5
test['Distanse_to_Hydrolody'] = (test['Horizontal_Distance_To_Hydrology']**2+test['Vertical_Distance_To_Hydrology']**2)**0.5

df['Hydro_Fire_1'] = df['Horizontal_Distance_To_Hydrology']+df['Horizontal_Distance_To_Fire_Points']
test['Hydro_Fire_1'] = test['Horizontal_Distance_To_Hydrology']+test['Horizontal_Distance_To_Fire_Points']

df['Hydro_Fire_2'] = abs(df['Horizontal_Distance_To_Hydrology']-df['Horizontal_Distance_To_Fire_Points'])
test['Hydro_Fire_2'] = abs(test['Horizontal_Distance_To_Hydrology']-test['Horizontal_Distance_To_Fire_Points'])

df['Hydro_Road_1'] = abs(df['Horizontal_Distance_To_Hydrology']+df['Horizontal_Distance_To_Roadways'])
test['Hydro_Road_1'] = abs(test['Horizontal_Distance_To_Hydrology']+test['Horizontal_Distance_To_Roadways'])

df['Hydro_Road_2'] = abs(df['Horizontal_Distance_To_Hydrology']-df['Horizontal_Distance_To_Roadways'])
test['Hydro_Road_2'] = abs(test['Horizontal_Distance_To_Hydrology']-test['Horizontal_Distance_To_Roadways'])

df['Fire_Road_1'] = abs(df['Horizontal_Distance_To_Fire_Points']+df['Horizontal_Distance_To_Roadways'])
test['Fire_Road_1'] = abs(test['Horizontal_Distance_To_Fire_Points']+test['Horizontal_Distance_To_Roadways'])

df['Fire_Road_2'] = abs(df['Horizontal_Distance_To_Fire_Points']-df['Horizontal_Distance_To_Roadways'])
test['Fire_Road_2'] = abs(test['Horizontal_Distance_To_Fire_Points']-test['Horizontal_Distance_To_Roadways'])


# plotc(df.Hillshade_3pm, df.Hillshade_Noon)

test_id = test['Id']
drops = ['Id']
for drop in drops:
    df = df.drop(drop,1)
    test = test.drop(drop,1)
train_X = df.drop('Cover_Type',1)
train_y = df['Cover_Type']

seed = 7
n_folds = 5
scoring = 'accuracy'
kfold = StratifiedKFold(train_y,shuffle=True,n_folds=n_folds,random_state=seed)

def modelfit(alg, train_X, train_y, performCV=True, printFeatureImportance=True, cv_folds=n_folds):
    #Fit the algorithm on the data
    alg.fit(train_X,train_y)
        
    #Predict training set:
    dtrain_predictions = alg.predict(train_X)
    dtrain_predprob = alg.predict_proba(train_X)[:,1]
    
    #Perform cross-validation:
    if performCV:
        cv_score = cross_val_score(alg, train_X, train_y, cv=cv_folds, scoring=scoring)
    
    #Print model report:
    print "\nModel Report"
    print "Accuracy : %.4g" % accuracy_score(y.values, dtrain_predictions)
    print "AUC Score (Train): %f" % roc_auc_score(y.values, dtrain_predprob)
    
    if performCV:
        print "CV Score : Mean - %.7g | Std - %.7g | Min - %.7g | Max - %.7g" % (np.mean(cv_score),np.std(cv_score),np.min(cv_score),np.max(cv_score))
        
    #Print Feature Importance:
    if printFeatureImportance:
        print pd.Series(alg.feature_importances_, predictors).sort_values(ascending=False)[:20]

param1 = {'n_estimators':[60,100,200]}
print 'haha'
gsearch1 = GridSearchCV(estimator=GradientBoostingClassifier(learning_rate=0.1,min_samples_split=500,min_samples_leaf=50,max_depth=8,max_features='sqrt',subsample=0.8,random_state=seed),
    param_grid = param1,scoring=scoring,cv=n_folds)
gsearch1.fit(train_X,train_y)
print gsearch1.grid_scores_
print gsearch1.best_params_
print gsearch1.best_score_


# gbm_grid = GradientBoostingClassifier(warm_start=True,random_state=seed,n_estimators=200,max_depth=8,max_features=20,learning_rate=0.1)


# et_grid = ExtraTreesClassifier(warm_start=True,random_state=seed,n_estimators=200,max_depth=None,max_features=20)
# model = VotingClassifier(estimators=[('gbm',gbm_grid),('et',et_grid)],voting='soft')
# model.fit(train_X,train_y)
# prob = model.predict(test)
# sub = pd.DataFrame(prob,columns=['Cover_Type'])
# sub['Id'] = test_id
# sub = sub[['Id','Cover_Type']]
# sub.to_csv('sub.csv',index=False)



