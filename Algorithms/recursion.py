import operator as op
import math
def ncr(n, k):
    r = min(k, n-k)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-k, -1))
    denom = reduce(op.mul, xrange(1, k+1))
    return numer//denom

def reg(n,k):
	if k==0:
		return '0'*n
	if k==n:
		return '1'*n
	if n<=2 and k==1:
		s = ''
		temp = ['0']*n
		for i in range(n):
			temp[i] = '1'
			s += ''.join(temp)
			temp[i] = '0'
			if i!= n-1:
				s += '+'
		return s

	result = []
	left = n/2
	right = int(math.ceil(n/2.0))
	start = max(0,k-right)
	end = min(left,k)
	for i in range(start,end+1):
		if left==i or i==0:
			result += list(reg(left,i))
		else:
			result.append('(')
			result += list(reg(left,i))
			result.append(')')
		if right==k-i or k-i==0:
			result += list(reg(right,k-i))
		else:
			result.append('(')
			result += list(reg(right,k-i))
			result.append(')')
		if i!= min(n/2,k):
			result.append('+')
	p = ''.join(result)
	
	return p

# import sys
# for line in sys.stdin:
# 	n = line.split()[0]
# 	k = line.split()[1]
# 	print reg(n,k)
a = 19
b = 1
s = reg(a,b)
print s
numbers = sum(c.isdigit() for c in s)
print numbers,ncr(a,b)*a+ncr(a,b)-1