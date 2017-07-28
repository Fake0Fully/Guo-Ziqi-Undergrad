import numpy as np
import rbm
import projectLib as lib
import pickle

training = lib.getTrainingData()
validation = lib.getValidationData()
# You could also try with the chapter 4 data
# training = lib.getChapter4Data()

trStats = lib.getUsefulStats(training)
vlStats = lib.getUsefulStats(validation)

K = 5

# mode = 'batch'
mode = 'single'

finalW = np.zeros([5,5,5])
finalRMSE = 100

def run_RBM(F, epochs, epsilon, B, weightcost, momentum, f, mode):
    # Initialise all our arrays
    W = rbm.getInitialWeights(trStats["n_movies"], F, K)
    bestW = np.zeros(W.shape)
    bestRMSE = 100

    posprods = np.zeros(W.shape)
    negprods = np.zeros(W.shape)
    grad = np.zeros(W.shape)

    for epoch in range(1, epochs):
        # in each epoch, we'll visit all users in a random order
        visitingOrder = np.array(trStats["u_users"])
        np.random.shuffle(visitingOrder)
        visitingOrder = np.array_split(visitingOrder, visitingOrder.shape[0] / B)
        # print(visitingOrder)
        for batch in visitingOrder:
            # print(batch)
            temp = np.zeros(W.shape)
            for user in batch:
                # get the ratings of that user
                ratingsForUser = lib.getRatingsForUser(user, training)
                # build the visible input
                v = rbm.getV(ratingsForUser)
                # get the weights associated to movies the user has seen
                ratingsWithBias = np.append(ratingsForUser[:,0],W.shape[0]-1)
                weightsForUser = W[ratingsWithBias, :, :]
                ### LEARNING ###
                # propagate visible input to hidden units


                posHiddenProb = rbm.visibleToHiddenVec(v, weightsForUser)

                # get positive gradient
                # note that we only update the movies that this user has seen!
                posprods[ratingsWithBias, :, :] += rbm.probProduct(v, posHiddenProb)



                ### UNLEARNING ###
                # sample from hidden distribution
                sampledHidden = rbm.sample(posHiddenProb)
                # propagate back to get "negative data"
                negData = rbm.hiddenToVisible(sampledHidden, weightsForUser)
                # propagate negative data to hidden units
                negData[-1,:] = np.array([1,1,1,1,1])
                negHiddenProb = rbm.visibleToHiddenVec(negData, weightsForUser)
                # get negative gradient
                # note that we only update the movies that this user has seen!
                negprods[ratingsWithBias, :, :] += rbm.probProduct(negData, negHiddenProb)
                # we average over the number of users
                delta = epsilon / epochs
                gradientLearningRate = epsilon - epoch * delta
                # print(gradientLearningRate)
                grad = momentum * grad + (1 - momentum) * gradientLearningRate * (
                    (posprods - negprods) / trStats['n_users'] - weightcost * np.linalg.norm(W))

                temp += grad
                # hiddenBiases += hiddenBiasGrad
                # visibleBiases += visibleBiasGrad
            W += temp

        # Print the current RMSE for training and validation sets
        # this allows you to control for overfitting e.g
        # We predict over the training set
        tr_r_hat = rbm.predict(trStats["movies"], trStats["users"], W, training)
        trRMSE = lib.rmse(trStats["ratings"], tr_r_hat)

        # We predict over the validation set
        vl_r_hat = rbm.predict(vlStats["movies"], vlStats["users"], W, training)
        vlRMSE = lib.rmse(vlStats["ratings"], vl_r_hat)

        if vlRMSE < bestRMSE:
            bestRMSE = vlRMSE
            bestW = W

        # if mode == 'single':
        print("### EPOCH %d ###" % epoch)
        print("Learning rate = %f" % gradientLearningRate)
        print("Training loss = %f" % trRMSE)
        print("Validation loss = %f" % vlRMSE)

        content_to_be_written = "" + str(F) + ", " + str(epoch) + ", " + str(epsilon) + ", " + str(B) + ", " + str(
            weightcost) + ", "
        content_to_be_written += str(momentum) + ", " + str(trRMSE) + ", " + str(vlRMSE) + '\n'
        f.write(content_to_be_written)

    # np.save('best_weight.npy', bestW)
    return (bestW,bestRMSE)


# SET PARAMETERS HERE!!!
# number of hidden units
F = 7
epochs = 2
epsilon = 0.001
B = 10
weightcost = 0.001
momentum = 0.3

range_F = [4,6,8,10,12,14]
range_Epsilon = [0.01,0.02,0.005]
range_B = [20,10]
range_weightcost = [0.0005,0.001]
range_momentum = [0.3,0.5]


f = open("log.csv", 'w')
f.write("F, epochs, epsilon, B, weightcost, momentum, trRSME, vlRSME\n")

if mode == 'batch':

    total = len(range_F) * len(range_Epsilon) * len(range_B) * len(range_weightcost) * len(range_momentum)
    count = 0
    for F in range_F:
        for epsilon in range_Epsilon:
            for B in range_B:
                for weightcost in range_weightcost:
                    for momentum in range_momentum:
                        count += 1
                        print("====== ", round(count/float(total)*100,2),"% =====")
                        print("F:        ",F)
                        print("epsilon:  ",epsilon)
                        print("B:        ", B)
                        print("weightcost", weightcost)
                        print("momentum: ", momentum)
                        results = run_RBM(F, epochs, epsilon, B, weightcost, momentum, f, mode)
                        if results[1] < finalRMSE:
                            finalRMSE = results[1]
                            finalW = results[0]

if mode == 'single':
    finalW = run_RBM(F, epochs, epsilon, B, weightcost, momentum, f, mode)[0]

f.close()


### END ###
# This part you can write on your own
# you could plot the evolution of the training and validation RMSEs for example
predictedRatings = np.array([rbm.predictForUser(user, finalW, training) for user in trStats["u_users"]])

np.savetxt("predictedRatings.txt", predictedRatings)
