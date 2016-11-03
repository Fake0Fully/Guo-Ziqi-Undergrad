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
from sklearn.metrics import log_loss
import xgboost as xgb

df = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')
df = df.drop('AnimalID',1)
IDs = test['ID']
test = test.drop('ID',1)
df = pd.concat([df,test],axis=0,keys=['train','test'])
# sns.countplot(df.AnimalType,palette='Set3')
# sns.countplot(df.OutcomeType,palette='Set3')
# sns.countplot(df.SexuponOutcome,palette='Set3')
# plt.show()

def get_sex(x):
	x = str(x)
	if x.find('Male') >= 0: return 'male'
	if x.find('Female') >= 0: return 'female'
	return 'unknown'
def get_neutered(x):
	x = str(x)
	if x.find('Sprayed') >= 0: return 'neutered'
	if x.find('Neutered') >= 0: return 'neutered'
	if x.find('Intact') >= 0: return 'intact'
	return 'unknown'

df['Sex'] = df.SexuponOutcome.apply(get_sex)
df['Neutered'] = df.SexuponOutcome.apply(get_neutered)

def get_mix(x):
	x = str(x)
	if x.find('Mix') >= 0: return 'mix'
	return 'not'
df['Mix'] = df.Breed.apply(get_mix)

def calc_age_in_days(x):
	x = str(x)
	if x == 'nan':return 0
	age = int(x.split()[0])
	if x.find('year') > -1: return age*365
	if x.find('month') > -1: return age*30
	if x.find('week') > -1: return age*7
	if x.find('day') > -1: return age
	else: return 0
df['AgeInDays'] = df.AgeuponOutcome.apply(calc_age_in_days)
df.loc[df['AgeInDays']==0,'AgeInDays'] = df.loc[df['AgeInDays']!=0,'AgeInDays'].mean()

def calc_age_category(x):
	if x < 50: return 'young'
	if x < 120: return 'young adult'
	if x < 900: return 'adult'
	if x < 1200: return 'older adult'
	return 'old'
df['AgeCategory'] = df.AgeInDays.apply(calc_age_category)

df.loc[df.Name.notnull(),'Name'] = 'named'
df.loc[df.Name.isnull(),'Name'] = 'nameless'

df['DateTime'] = pd.to_datetime(df['DateTime'])
df['Year'] = df['DateTime'].dt.year
df['Month'] = df['DateTime'].dt.month
df['Day'] = df['DateTime'].dt.day
df['DayofWeek'] = df['DateTime'].dt.dayofweek
df['DayofYear'] = df['DateTime'].dt.dayofyear
df['TimeinDay'] = pd.cut(df['DateTime'].dt.hour,3,labels=['morning','afternoon','evening'])

rare_color = df['Color'].value_counts().sort_values().index.values[:-100]
df.loc[df['Color'].isin(rare_color),'Color'] = 'Rare'

rare_breed = df.loc[df['AnimalType']=='Dog','Breed'].value_counts().sort_values().index.values[:-100]
df.loc[df['Breed'].isin(rare_breed),'Breed'] = 'Rare'

drops = ['OutcomeSubtype','AgeuponOutcome','DateTime','SexuponOutcome']
for drop in drops:
    df = df.drop(drop, 1)

categorical_vars = ['AnimalType','TimeinDay','Neutered','Sex','Mix','Breed','AgeCategory','Name','Year','Month','Day','DayofWeek','Color']
for var in categorical_vars:
    df = pd.concat([df, pd.get_dummies(df[var], prefix=var)], 1)
    df = df.drop(var,1)

X = df.ix['train'].drop('OutcomeType',1)
y = df.ix['train']['OutcomeType']
test = df.ix['test'].drop('OutcomeType',1)

models = []
models.append(('LR',LogisticRegression()))
models.append(('KNN',KNeighborsClassifier(n_neighbors=5)))
models.append(('RF',RandomForestClassifier()))
models.append(('NB',GaussianNB()))

results = []
names = []

seed = 7
n_folds = 5
n_ins = len(X)
scoring = 'log_loss'
kfold = StratifiedKFold(y,n_folds=n_folds,shuffle=True,random_state=seed)

# for name,model in models:
#    cv_results = cross_val_score(model,X,y,cv=kfold,scoring=scoring)
#    results.append(cv_results)
#    names.append(name)
#    print("{0}: ({1:.3f}) +/- ({2:.3f})".format(name, cv_results.mean(), cv_results.std()))

# def cv_optimize(clf,parameters,Xtrain,ytrain,n_folds=kfold,score=scoring):
#     gs = GridSearchCV(clf,param_grid=parameters,cv=n_folds,scoring=score)
#     gs.fit(Xtrain,ytrain)
#     print 'BEST PARAMS',gs.best_params_
#     results = cross_val_score(gs.best_estimator_, Xtrain, ytrain, cv=kfold, scoring=scoring)
#     print("({0:.6f}) +/- ({1:.6f})".format(results.mean(), results.std()))
#     best = gs.best_estimator_
#     return best

# rf_grid = cv_optimize(
#     RandomForestClassifier(n_estimators = 400,warm_start=True,random_state=seed),
#     parameters = {
#         'criterion':['entropy'],
#         'max_features':['sqrt'],
#         'max_depth':[15,20]
#         },
#     Xtrain = X, ytrain = y)

# et_grid = cv_optimize(
# 	ExtraTreesClassifier(n_estimators = 400,warm_start=True,random_state=seed),
# 	parameters = {
# 		'criterion':['entropy'],
# 		'max_features':['sqrt'],
# 		'max_depth':[15,20]
# 	},
# 	Xtrain = X, ytrain = y)

num_round = 1000

param1 = {'max_depth':7, 'learning_rate':0.1, 'silent':0, 'objective':'multi:softprob','num_class':5,
        'eval_metric':'mlogloss','subsample':0.75,'colsample_bytree':0.85,'reg_lambda':1,'n_estimators':num_round}

param2 = {'max_depth':6, 'learning_rate':0.1, 'silent':0, 'objective':'multi:softprob','num_class':5,
        'eval_metric':'mlogloss','subsample':0.85,'colsample_bytree':0.75,'reg_lambda':1,'n_estimators':num_round}

param3 = {'max_depth':8, 'learning_rate':0.03, 'silent':0, 'objective':'multi:softprob','num_class':5,
        'eval_metric':'mlogloss','subsample':0.65,'colsample_bytree':0.75,'reg_lambda':1,'n_estimators':num_round}

param4 = {'max_depth':9, 'learning_rate':0.03, 'silent':0, 'objective':'multi:softprob','num_class':5,
        'eval_metric':'mlogloss','subsample':0.55,'colsample_bytree':0.65,'reg_lambda':1,'n_estimators':num_round}

param5 = {'max_depth':12, 'learning_rate':0.03, 'silent':0, 'objective':'multi:softprob','num_class':5,
        'eval_metric':'mlogloss','subsample':1,'colsample_bytree':1,'reg_lambda':1,'n_estimators':num_round}

bst1 = xgb.XGBClassifier(param1)
bst2 = xgb.XGBClassifier(param2)
bst3 = xgb.XGBClassifier(param3)
bst4 = xgb.XGBClassifier(param4)
bst5 = xgb.XGBClassifier(param5)

# prob = (bst1.predict(test) + bst2.predict(test) + bst3.predict(test) +  bst4.predict(test) +  bst5.predict(test))/5

model = VotingClassifier(estimators=[('xgb1',bst1),('xgb2',bst2),('xgb3',bst3),('xgb4',bst4),('xgb5',bst5)],voting='soft')
model.fit(X,y)
prob = model.predict_proba(test)
sub = pd.DataFrame(prob,columns=['Adoption','Died','Euthanasia','Return_to_owner','Transfer'])
sub['ID'] = IDs
sub = sub[['ID','Adoption','Died','Euthanasia','Return_to_owner','Transfer']]
sub.to_csv('sub.csv',index=False)
