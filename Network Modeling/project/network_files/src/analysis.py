# Authors:
# Guo Ziqi (1000905)
# Liu Sidian (1000909)
# Zhu Liying (1000922)
import zen
from numpy import *
import scipy
import numpy.linalg as la
import matplotlib.pyplot as plt
plt.ioff()
import sys
sys.path.append('../zend3js')
from time import sleep
import d3js
import csv
import copy

def modularity(G,c):
	d = dict()
	for k,v in c.iteritems():
		for n in v:
			d[n] = k
	Q, Qmax = 0,1
	for u in G.nodes_iter():
		for v in G.nodes_iter():
			if d[u] == d[v]:
				Q += ( int(G.has_edge(v,u)) - G.in_degree(u)*G.out_degree(v)/float(G.num_edges) )/float(G.num_edges)
				Qmax -= ( G.in_degree(u)*G.out_degree(v)/float(G.num_edges) )/float(G.num_edges)
	return Q, Qmax

def degree_covariance(G):
	cov = 0
	covmax = 0
	for u in G.nodes_iter():
		for v in G.nodes_iter():
			cov += (int(G.has_edge(v,u)) - G.in_degree(u)*G.out_degree(v)/float(G.num_edges))*G.in_degree(u)*G.out_degree(v)/float(G.num_edges)
			covmax += (G.in_degree(u)*int(G.in_degree(u)==G.out_degree(v))-G.in_degree(u)*G.out_degree(v)/float(G.num_edges))*G.in_degree(u)*G.out_degree(v)/float(G.num_edges)
	return cov,covmax

def find_kcore(k,G):
	switch = 0
	while switch==0 and G.num_nodes>0:
		switch = 1
		for i in G.nodes():
			if G.degree(i) < k:
				switch = 0
				G.rm_node(i)

def reciprocity(G):
	A = G.matrix()
	diag = trace(dot(A,A))
	return diag/G.num_edges

def bibliography(R):
    R_bb=zen.Graph()
    n=R.num_nodes
    for l in range(n):
        R_bb.add_node(R.node_object(l))
    for i in range(n):
        nbrs_i=set(R.out_neighbors_(i))
        for j in range(i+1,n):
            nbrs_j=set(R.out_neighbors_(j))
            common=nbrs_i.intersection(nbrs_j)
            if len(common)>0:
               R_bb.add_edge(R.node_object(i),R.node_object(j),weight=len(common))
    return R_bb

def cocitation(G):
    CG = zen.Graph()
    d = []
    for i in G.nodes():
        if len(G.in_neighbors(i))!=0:
            d.append(i)

    for i in G.nodes():
        CG.add_node(i)
        
    for i in d:
        for j in d:
            if i!=j:
                a = G.in_neighbors(i)
                b = G.in_neighbors(j)
                c = set(a).intersection(b)
                if len(c)!=0:
                    if CG.has_edge(i,j)==False:
                        CG.add_edge(i,j,weight=len(c))
    return CG

def edge_print_top(G,v, num=5):
	idx_list = [(i,v[i]) for i in range(len(v))]
	idx_list = sorted(idx_list, key = lambda x: x[1], reverse=True)
	for i in range(min(num,len(idx_list))):
		nidx, score = idx_list[i]
		anode, bnode = G.endpoints(nidx)
		print '  %i. %s.%s (%1.4f)' % (i+1,anode,bnode,score)

def edge_country_print_top(G,v,country,num=5):
	idx_list = [(i,v[i]) for i in range(len(v))]
	idx_list = sorted(idx_list, key = lambda x: x[1], reverse=True)
	new_list = []
	for i in idx_list:
		if country in G.endpoints(i[0]):
			new_list.append(i)
	for i in range(min(num,len(new_list))):
		nidx, score = new_list[i]
		anode, bnode = G.endpoints(nidx)
		print '  %i. %s.%s (%1.4f)' % (i+1,anode,bnode,score)

def print_top(G,v, num=5):
	idx_list = [(i,v[i]) for i in range(len(v))]
	idx_list = sorted(idx_list, key = lambda x: x[1], reverse=True)
	for i in range(min(num,len(idx_list))):
		nidx, score = idx_list[i]
		print '  %i. %s (%1.4f)' % (i+1,G.node_object(nidx),score)

def index_of_max(v):
	return where(v == max(v))[0]

def calc_powerlaw(G,kmin,kmax=None,plot=False):
	ddist = zen.degree.ddist(G,normalize=False)
	cdist = zen.degree.cddist(G,inverse=True)
	k = arange(len(ddist))
	
	if plot==True:
		plt.figure(figsize=(8,12))
		plt.subplot(211)
		plt.bar(k,ddist, width=0.8, bottom=0, color='b')
		plt.subplot(212)
		plt.loglog(k,cdist)
		plt.show()
	
	a = 0
	if kmax==None:
		kmax = k[-1]
		N = int(cdist[kmin]*G.num_nodes)
	else:
		N = int(cdist[kmin]*G.num_nodes - cdist[kmax+1]*G.num_nodes)
	for i in G.nodes_iter():
		if G.degree(i) >= kmin and G.degree(i) <= kmax:
			a += log(G.degree(i)/(kmin-0.5))	
	alpha = 1 + N*(1/a) # calculate using (8.6)!
	sigma = (alpha-1)/sqrt(N) # calculate using (8.7)!
	print 'Alpha is %1.2f +/- %1.2f' % (alpha,sigma)

def modularity_max_simple(G):
	print 'maximizing...'
	group = {}
	for i in G.nodes_iter():
		if group.has_key(G.node_data(i)['zenData'])==False:
			group[G.node_data(i)['zenData']]=[i]
		else:
			group[G.node_data(i)['zenData']].append(i)
	ng = {'C1':[],'C2':[]}
	for key in group.keys():
		if key in ['Caribbean','Asia','Africa','South America','Middle East']:
			ng['C1']+=group[key]
		else:
			ng['C2']+=group[key]

	flag = 0
	while flag == 0:
		flag = 1
		best = [0,0]
		base = modularity(G,ng)[0]/modularity(G,ng)[1]
		print 'Updated Assortativity Coeff: %1.4f' % base
		for i in range(len(ng['C1'])):
			rep = copy.deepcopy(ng)
			temp = rep['C1'][i]
			del(rep['C1'][i])
			rep['C2'].append(temp)
			a = modularity(G,rep)
			b = a[0]/a[1]
			if b > base:
				base = b
				best = (1,i)
				print 'Current best: moving %i from 1 to 2' % best[1]
				flag = 0
		for i in range(len(ng['C2'])):
			rep = copy.deepcopy(ng)
			temp = rep['C2'][i]
			del(rep['C2'][i])
			rep['C1'].append(temp)
			a = modularity(G,rep)
			b = a[0]/a[1]
			if b > base:
				base = b
				best = (2,i)
				print 'Current best: moving %i from 2 to 1' % best[1]
				flag = 0
		if best[0]==1:
			print 'Moving one node from group 1 to 2...'
			temp = ng['C1'][best[1]]
			del(ng['C1'][best[1]])
			ng['C2'].append(temp)
		elif best[0]==2:
			print 'Moving one node from group 2 to 1...'
			temp = ng['C2'][best[1]]
			del(ng['C2'][best[1]])
			ng['C1'].append(temp)
		else:
			continue
	output = []
	for i in ng['C1']:
		output.append([i,1])
	for i in ng['C2']:
		output.append([i,2])
	print '\nSimple Modularity Maximization:'
	print 'Modularity: %1.4f' % G.modularity(G,ng)[0]
	print 'Assortativity Coefficient: %1.4f' % G.modularity(G,ng)[0]/G.modularity(G,ng)[1]
	
def write_csv(file,a):
	with open(file,'wb') as f:
		writer = csv.writer(f)
		writer.writerows(a)



G = zen.io.gml.read('projectvisa.gml',directed=True)

print '================Explore Singapore================'
print 'Singapore in-degree: %i' % G.in_degree('Singapore')
print 'Singapore out-degree: %i\n' % G.out_degree('Singapore')

print '============Degree Distribution and Power Law============'
m = G.num_edges
n = G.num_nodes
c = m/n
d = zen.diameter(G)
print 'Number of nodes: %i' % m
print 'Number of edges: %i' % n
print 'Mean in/out-degree: %1.2f'% c
print 'Diameter: %i' % d
rho = c/float(n-1)
print 'Density: %1.4f' % rho
calc_powerlaw(G,196,plot=False)
degree = []

print '\n===================Clustering==================='
print 'Global Clustering Coefficient: %1.4f' % (zen.algorithms.clustering.gcc(G))
print 'Average Local Clustering Coefficient: %1.4f' % (zen.algorithms.clustering.ncc(G))

print '\n===================Reciprocity==================='
print 'Reciprocity: %1.4f' % (reciprocity(G))
a = G.in_neighbors('Singapore')
b = G.out_neighbors('Singapore')
recip = set(a).intersection(set(b))
print 'Countries that are reciprocal with Singapore:'
print list(recip)

print '\n================Cocitation Network================'
print 'Top 5 Edges in Cocitation Network:'
v=[]
C = cocitation(G)
for i in C.edges_iter_():
    v.append(C.weight_(i))
edge_print_top(C,v)
print '\nTop 5 Edges connecting Singapore in Cocitation Network'
edge_country_print_top(C,v,country='Singapore')

print '\n================Bibliographic Network================'
print 'Top 5 Edges in Bibliographic Network:'
v = []
B = bibliography(G)
for i in B.edges_iter_():
    v.append(B.weight_(i))
edge_print_top(B,v)
print '\nTop 5 Edges connecting Singapore in Bibliographic Network'
edge_country_print_top(B,v,country='Singapore')

print '\n===================K-Core==================='
GG = G.skeleton()
k = 86
find_kcore(k,GG)
print 'The largest K-core available: k=%i, covering %i vertices' % (k,GG.num_nodes)

print '\n=================Degree Centrality================='
A = G.matrix()
N = G.num_nodes
print "Degree Centrality Top 5:"
print "In-degree:"
v = []
for i in G.nodes():
	v.append(G.in_degree(i))
print_top(G,v,num=5)
print "Out-degree:"
v = []
for i in G.nodes():
	v.append(G.out_degree(i))
print_top(G,v,num=5)

print '\n=================Eigenvector Centrality================='
print 'In-degree(right eigenvector):'
A = G.matrix()
evalue = abs(la.eig(A.transpose())[0])
evector = abs(la.eig(A.transpose())[1].transpose())
i = index_of_max(evalue)
print_top(G,evector[i].transpose(), num=5)
print 'Out-degree(left eigenvector):'
v = zen.algorithms.centrality.eigenvector_centrality_(G,weighted=False)
print_top(G,v,num=5)

print '\n====================Katz Centrality======================'
print 'In-degree(right eigenvector):'
A = G.matrix()
N = G.num_nodes
evalue = abs(la.eig(A.transpose())[0])
evector = abs(la.eig(A.transpose())[1].transpose())
i = index_of_max(evalue)
B = ones((N,1))
I = identity(N)
a = 1/(evalue[i]+1)
vin = dot(la.inv(I-a*A.transpose()),B)
print_top(G,vin,num=5)
print 'Out-degree(left eigenvector):'
vout = dot(la.inv(I-a*A),B)
print_top(G,vout,num=5)

print '\n==================PageRank Centrality==================='
print 'In-degree(right eigenvector):'
V = []
for i in G.nodes():
	V.append(max(1,G.in_degree(i)))
D = diag(V)
a = 0.85
vin = dot(dot(D,la.inv(D-dot(a,A.transpose()))),B)
print_top(G,vin,num=5)
print 'Out-degree(left eigenvector):'
vout = dot(dot(D,la.inv(D-dot(a,A))),B)
print_top(G,vout,num=5)

print '\n=================Betweeness Centrality==================='
v=zen.algorithms.centrality.betweenness_centrality_(G)
print_top(G,v,num=5)

print '\n==========Assortativity Mixing(Enumerative)============'
group = {}
for i in G.nodes_iter():
	if group.has_key(G.node_data(i)['zenData'])==False:
		group[G.node_data(i)['zenData']]=[i]
	else:
		group[G.node_data(i)['zenData']].append(i)
Q, Qmax = modularity (G,group)
print 'Group by regions:'
print '  Modularity: %1.4f / %1.4f' % (Q,Qmax)
print '  Assortativity Coefficient: %1.4f' % (Q/Qmax)

combined_group = {'Developed':[],'Developing':[]}
for key in group.keys():
	if key in ['Caribbean','Asia','Africa','South America','Middle East']:
		combined_group['Developing']+=group[key]
	else:
		combined_group['Developed']+=group[key]
Q, Qmax = modularity (G,combined_group)
print '\nGroup by development:'
print '  Modularity: %1.4f / %1.4f' % (Q,Qmax)
print '  Assortativity Coefficient: %1.4f' % (Q/Qmax)

africa_group = {'Africa':[],'Non-Africa':[]}
for key in group.keys():
	if key=='Africa':
		africa_group['Africa']+=group[key]
	else:
		africa_group['Non-Africa']+=group[key]
Q, Qmax = modularity (G,africa_group)
print '\nGroup by Africa:'
print '  Modularity: %1.4f / %1.4f' % (Q,Qmax)
print '  Assortativity Coefficient: %1.4f' % (Q/Qmax)

print '\n===============Assortative Mixing(Degree)================='
cov,covmax = degree_covariance(G)
print 'Degree Covariance: %1.4f' % cov
print 'Correlaton Coefficient: %1.4f' % (cov/covmax)

print '\n================Modularity Maximization=================='
A = G.matrix()
n = G.num_nodes
m = G.num_edges
B = identity(n)
for i in range(n):
	for j in range(n):
		B[i,j]=A[i,j]-G.in_degree_(i)*G.out_degree_(j)/m
val = la.eig(B)[0]
vec = la.eig(B)[1].transpose()
i = index_of_max(val)
v = vec[i].transpose()
positive=[]
negative=[]
group = {'community1':[],'community2':[]}
for i in range(len(v)):
	if v[i]>0:
		positive.append(i)
   	else:
   		negative.append(i)
for i in positive:
   	group['community1'].append(G.node_object(i))
for i in negative:
   	group['community2'].append(G.node_object(i))
Q,Qmax = modularity(G,group)
print 'Spectral Modularity Maximization:'
print 'Modularity: %1.4f' %(Q)
print 'Modularity Coefficient: %1.4f' %(Q/Qmax)


# Simple Modularity Maximization:
# Returned an assortativity coefficient of 0.3425
# Runtime is 1702 seconds
# modularity_max_simple(G)








