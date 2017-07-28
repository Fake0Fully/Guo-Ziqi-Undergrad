import numpy as np
import copy

r = np.array([29.07, 31.2, 34.22, 35.12, 37.32, 37.83, 42.58, 43.55, 48.52, 53.42, 58.05, 63.28, 63.33, 63.42, 64.45])
p = np.array([[17, 18, 23, 15, 23, 17, 9, 13, 19, 19, 18, 16, 10, 6, 24],[20, 13, 21, 24, 15, 14, 19, 19, 21, 18, 23, 18, 23, 15, 19]])

rr = copy.deepcopy(r)
pp = copy.deepcopy(p)

time = 0
schedule = [[],[]]

comp1 = r
nxt1 = int(np.where(comp1 == min(comp1))[0])
comp2 = r
nxt2 = int(np.where(comp2 == min(comp2))[0])
completion = np.array([comp1,comp2])

wait = 0

if nxt1 < nxt2:
	schedule[0].append(nxt1)
	nxt = [0,nxt1,completion[0][nxt1]]
	rr = np.delete(rr, nxt1, 0)
	pp = np.delete(pp, nxt1, 1)

	compp2 = rr
	temp = int(np.where(compp2 == min(compp2))[0])
	nxt2 = int(np.where(comp2 == min(compp2))[0])
	schedule[1].append(nxt2)
	rr = np.delete(rr, temp, 0)
	pp = np.delete(pp, temp, 1)
	nxtt = [1,nxt2,completion[1][nxt2]]
else:
	schedule[1].append(nxt2)
	nxt = [1,nxt2,completion[1][nxt2]]
	rr = np.delete(rr, nxt2, 0)
	pp = np.delete(pp, nxt2, 1)

	compp1 = rr
	temp = int(np.where(compp1 == min(compp1))[0])
	nxt1 = int(np.where(comp1 == min(compp1))[0])
	schedule[0].append(nxt1)
	rr = np.delete(rr, temp, 0)
	pp = np.delete(pp, temp, 1)
	nxtt = [0,nxt1,completion[0][nxt1]]

total = 0

while len(schedule[0])+len(schedule[1]) < 15:
	time = nxt[2]
	total += time
	comp = rr
	job = int(np.where(completion[nxt[0]] == min(comp))[0])
	temp = int(np.where(comp == min(comp))[0])
	rr = np.delete(rr, temp, 0)
	pp = np.delete(pp, temp, 1)
	schedule[nxt[0]].append(job)

	expected = max(r[job],time) + p[nxt[0]][job]
	wait = max(max(time - r[job], 0), wait)
	

	if nxtt[2] <= expected:
		nxt = nxtt
		nxtt = [1-nxt[0],job,expected]
	else:
		nxt = [nxt[0],job,expected]
	# print nxt,nxtt

total += nxt[2] + nxtt[2]
print schedule
print nxtt[2]
print wait
print total





