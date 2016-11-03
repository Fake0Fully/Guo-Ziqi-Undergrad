import numpy as np
import pandas as pd
from sklearn.cross_validation import KFold,cross_val_score,train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import accuracy_score,confusion_matrix
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
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

def get_hybrid(x):
	hybrid = x[(x.network!='sw') & (x.network!='reg')]
	return hybrid
# df = get_hybrid(df)

y = df['network']
yc = df_c['network']
X = df.drop('network',1)
Xc = df_c.drop('network',1)
X = preprocessing.scale(X) # Standardization
print X
Xc = preprocessing.scale(Xc)
labels = y.unique()
n_folds = 10
n_ins = len(X)
kfold = KFold(n=n_ins,shuffle=True,n_folds=n_folds,random_state=seed)
split = 0.3

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=split,random_state=seed)
Xc_train,Xc_test,yc_train,yc_test = train_test_split(Xc,yc,test_size=split,random_state=seed)


# models = []
# models.append(('LR',LogisticRegression()))
# models.append(('KNN',KNeighborsClassifier(n_neighbors=5)))
# models.append(('RF',RandomForestClassifier()))
# models.append(('NB',GaussianNB()))
# models.append(('SVM',SVC(C=10,kernel='linear')))

# results = []
# names = []
# for name,model in models:
#    cv_results = cross_val_score(model,X,y,cv=n_folds,scoring='accuracy')
#    results.append(cv_results)
#    names.append(name)
#    print("{0}: ({1:.3f}) +/- ({2:.3f})".format(name, cv_results.mean(), cv_results.std()))

def cv_optimize(clf,parameters,Xtrain,ytrain,n_folds=kfold,score='accuracy'):
    gs = GridSearchCV(clf,param_grid=parameters,cv=n_folds,scoring=score)
    gs.fit(Xtrain,ytrain)
    print 'BEST PARAMS',gs.best_params_
    best = gs.best_estimator_
    results = cross_val_score(gs.best_estimator_, Xtrain, ytrain, cv=n_folds, scoring=score)
    print("({0:.6f}) +/- ({1:.6f})".format(results.mean(), results.std()))
    return best

# svm_grid = cv_optimize(
#     SVC(random_state=seed,kernel='linear'),
#     parameters = {
#         'C':[10]},
#     Xtrain = X,ytrain = y)

rf_grid = cv_optimize(
    RandomForestClassifier(warm_start=True,random_state=seed),
    parameters = {
        'n_estimators':[100,150],
        'criterion':['gini'],
        'max_features':[5,10,20],
        'max_depth':[2,5,10],
        'bootstrap':[True]},
    Xtrain = X,ytrain = y)
model = rf_grid
model.fit(X_train,y_train)

pred = model.predict(X_test)
print accuracy_score(y_test,pred)
print('Confusion matrix, without normalization')
cm = confusion_matrix(y_test,pred)

def plot_confusion_matrix(cm, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=45)
    plt.yticks(tick_marks, labels)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

print(cm)
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
print('Normalized confusion matrix')
print(cm_normalized)
plt.figure()
plot_confusion_matrix(cm_normalized, title='Normalized confusion matrix')
# plt.show()



