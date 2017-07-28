set J; 				#jobs
set I;				#machines
set K;				#positions
param p{I,J};		#processing time of job j on machine i
param r{J};			#release time of job j
param M;			#big M
var x{I,J,K} binary;#job j on machine i in position k
var h{I,K};			#completion time of position k on machine i
var c{I,J};			#completion time of job j on machine i
var cmax;

minimize makespan: cmax;

subject to job {j in J}: sum{i in I} sum{k in K} x[i,j,k] = 1;

subject to position {i in I, k in K}: sum{j in J} x[i,j,k] <= 1;

subject to pCompletionAfterR {i in I, k in K}: h[i,k] >= sum{j in J} (p[i,j] + r[j] ) * x[i,j,k];

subject to noOverlap {i in I, k in K: k > 1}: h[i,k] >= h[i,k-1] + sum{j in J} p[i,j] * x[i,j,k];

subject to boundMakespan {i in I, k in K}: cmax >= h[i,k];

subject to positionStartFrom1 {i in I, k in K: k > 1}: sum{j in J} x[i,j,k] <= sum{j in J} x[i,j,k-1];



