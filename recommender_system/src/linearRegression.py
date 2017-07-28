import numpy as np
import projectLib as lib
from numpy.linalg import pinv
import matplotlib.pyplot as plt
# shape is movie,user,rating
training = lib.getTrainingData()
validation = lib.getValidationData()
# training = np.concatenate([training, validation])



#some useful stats
trStats = lib.getUsefulStats(training)
vlStats = lib.getUsefulStats(validation)

rBar = np.mean(trStats["ratings"])

# we get the A matrix from the training dataset
def getA(training):
    A = np.zeros((trStats["n_ratings"], trStats["n_movies"] + trStats["n_users"]))
    # ???
    for i in range(trStats["n_ratings"]) :
        x=training[i]
        movieId = x[0]
        userId =x[1]
        userIndex = trStats["n_movies"]+userId
        A[i][movieId]=1.0
        A[i][userIndex]=1
    return A

# we also get c
def getc(rBar, ratings):
    # ???
    c = np.zeros(trStats["n_ratings"])
    for i in range(trStats["n_ratings"]):
        c[i]=ratings[i]-rBar
    return c

# apply the functions
A = getA(training)
c = getc(rBar, trStats["ratings"])

# compute the estimator b
def param(A, c):
    b = np.dot(np.dot(pinv(np.dot(A.transpose(), A)), A.transpose()),c)
    return b

# compute the estimator b with a regularisation parameter l
# note: lambda is a Python keyword to define inline functions
#       so avoid using it as a variable name!
def param_reg(A, c, l):
    b = np.dot(np.dot(pinv(np.dot(A.transpose(), A)+l*np.identity(A.shape[1])), A.transpose()),c)
    return b

# from b predict the ratings for the (movies, users) pair
def predict(movies, users, rBar, b):
    n_predict = len(users)
    p = np.zeros(n_predict)
    for i in range(0, n_predict):
        rating = rBar + b[movies[i]] + b[trStats["n_movies"] + users[i]]
        if rating > 5: rating = 5.0
        if rating < 1: rating = 1.0
        p[i] = rating
    return p

# Unregularised version
#b = param(A, c)

# Regularised version
lambdaList = []
rmseList = []
bestLambda = 0
bestRMSE = 100

for i in range(40,90):
    l = i*0.1
    b = param_reg(A, c, l)

    trRMSE = lib.rmse(predict(trStats["movies"], trStats["users"], rBar, b), trStats["ratings"])
    vlRMSE = lib.rmse(predict(vlStats["movies"], vlStats["users"], rBar, b), vlStats["ratings"])

    lambdaList.append(l)
    rmseList.append(vlRMSE)

    if bestRMSE > vlRMSE:
        bestRMSE = vlRMSE
        bestLambda = l

    print("Linear regression, l = %f" % l)
    print("Training loss = %f" % trRMSE)
    print("Validation loss = %f\n" % vlRMSE)
print(bestRMSE, bestLambda)

# plt.plot(lambdaList, rmseList, lambdaList,trainList)
# plt.ylabel('Validation RMSE')
# plt.xlabel('Lambda')
# plt.xticks(np.arange(min(lambdaList), max(lambdaList)+1, 0.5))
# plt.show()

b = param_reg(A,c,6.7)
results = []
for i in trStats['u_users']:
    results.append(predict(trStats['u_movies'],[i]*trStats['n_movies'],rBar,b))
results = np.array(results)
np.savetxt("predictedRatings.txt", results)
