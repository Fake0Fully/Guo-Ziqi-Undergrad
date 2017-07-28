set J; 				#jobs
set I;				#machines
set K;				#positions
param p{I,J};		#processing time of job j on machine i
param r{J};			#release time of job j
param M;
var x{I,J,K} binary;#job j on machine i in position k
var h{I,K};			#completion time of position k on machine i
var c{I,J};			#completion time of job j on machine i
var cmax;			#makespan
var wmax;			#maximum waiting time
var wwmax;			#maximum weighted waiting time
var w{I,J,K};		#waiting time of job j on machine i on position k
var ww{I,J};		#weighted waiting time of job j on machine i on position k


minimize makespan: wmax;

subject to set0 {i in I, j in J, k in K: p[i,j]=2000}: x[i,j,k] = 0;

subject to job {j in J}: sum{i in I} sum{k in K} x[i,j,k] = 1;

subject to position {i in I, k in K}: sum{j in J} x[i,j,k] <= 1;

subject to pCompletionAfterR {i in I, k in K}: h[i,k] >= sum{j in J} (p[i,j] + r[j] ) * x[i,j,k];

subject to noOverlap {i in I, k in K: k > 1}: h[i,k] >= h[i,k-1] + sum{j in J} p[i,j] * x[i,j,k];

subject to boundMakespan {i in I, k in K}: cmax >= h[i,k];

subject to no2000 {i in I, k in K}: h[i,k]<=1999;

subject to positionStartFrom1 {i in I, k in K: k > 1}: sum{j in J} x[i,j,k] <= sum{j in J} x[i,j,k-1];

subject to waitingTime {i in I, j in J, k in K: k > 1}: w[i,j,k] >= h[i,k-1] - r[j] - M * (1-x[i,j,k]);

subject to maxWaiting {i in I, j in J, k in K}: wmax >= w[i,j,k];

subject to 0waiting {i in I , j in J, k in K}: w[i,j,k] <= M*x[i,j,k];

subject to bigger0 {i in I , j in J, k in K}: w[i,j,k]>=0;

subject to weightedWaiting {i in I, j in J}: ww[i,j] = (sum{k in K} w[i,j,k]) / p[i,j];

subject to maxWW {i in I, j in J}: wwmax >= ww[i,j];

