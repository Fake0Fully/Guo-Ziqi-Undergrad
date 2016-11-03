def expectation(a,b):
	return (a+1.0)/(a+b+2.0)

def truncate(f,n):
	sp = str(f).split('.')
	return '.'.join([sp[0],sp[1][:3]])

def bandit(s,a1,b1,a2,b2,d):
	if s=='GC':
		e1 = expectation(a1,b1)
		e2 = expectation(a2,b2)
		if e1>=e2:
			return 1
		else:
			return 2
	if s=='OR' and d==0:
		return '0'
	if s=='GR':	
		if d==0:
			return 0	
		gree = [[[[[] for i in range(d+1)] for i in range(d+1)] for i in range(d+1)] for i in range(d+1)]
		for i in range(0,d+1):
			for e in range(0,d-i+1):
				for f in range(0,d-i-e+1):
					for g in range(0,d-i-e-f+1):
						h = d-i-e-f-g
						if i==0:
							gree[e][f][g][h]=0.0
						else:
							aa1 = a1 + e
							bb1 = b1 + f
							aa2 = a2 + g
							bb2 = b2 + h
							e1 = expectation(aa1,bb1)
							e2 = expectation(aa2,bb2)
							if e1>=e2:
								r = e1*(1+gree[e+1][f][g][h])+(1-e1)*gree[e][f+1][g][h]
							else:
								r = e2*(1+gree[e][f][g+1][h])+(1-e2)*gree[e][f][g][h+1]
							gree[e][f][g][h] = r
		return truncate(gree[0][0][0][0],3)
	else:
		opt = [[[[[] for i in range(d+1)] for i in range(d+1)] for i in range(d+1)] for i in range(d+1)]
		for i in range(0,d+1):
			for e in range(0,d-i+1):
				for f in range(0,d-i-e+1):
					for g in range(0,d-i-e-f+1):
						h = d-i-e-f-g
						if i==0:
							opt[e][f][g][h]=0.0
						else:
							aa1 = a1 + e
							bb1 = b1 + f
							aa2 = a2 + g
							bb2 = b2 + h
							e1 = expectation(aa1,bb1)
							r1 = e1*(1+opt[e+1][f][g][h])+(1-e1)*opt[e][f+1][g][h]
							e2 = expectation(aa2,bb2)
							r2 = e2*(1+opt[e][f][g+1][h])+(1-e2)*opt[e][f][g][h+1]
							opt[e][f][g][h] = max(r1,r2)
		if s=='OR':
			return truncate(opt[0][0][0][0],3)
		else:
			e1 = expectation(a1,b1)
			e2 = expectation(a2,b2)
			r1 = e1*(1+opt[1][0][0][0])+(1-e1)*opt[0][1][0][0]
			r2 = e2*(1+opt[0][0][1][0])+(1-e2)*opt[0][0][0][1]
			if r1>=r2:
				return 1
			else:
				return 2


import sys
for line in sys.stdin:
	s = line.split()[0]
	a1 = int(line.split()[1])
	b1 = int(line.split()[2])
	a2 = int(line.split()[3])
	b2 = int(line.split()[4])
	d = int(line.split()[5])
	print bandit(s,a1,b1,a2,b2,d)





