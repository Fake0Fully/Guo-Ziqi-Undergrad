import numpy as np
import random

# Analytical Approach
def P(n, p):
	prob = [1,1]
	for i in range(n-1):
		next = p*prob[-1] + p*(1-p)*prob[-2]
		prob.append(next)
	return prob[-1]

print P(82, 0.8)


# Simulation Approach
yes = 0
trials = 100000
random.seed(1)
for i in range(trials):
	season = np.random.choice([0,1], 82, p=[0.8,0.2])
	if any(season[i]==season[i+1] and season[i]==1 for i in range(len(season)-1)):
		yes += 1

print 1 - yes / float(trials)