import urllib2
import scipy
import scipy.stats
from math import erf
from math import sqrt
from collections import Counter

def cerf(x):
	return 1-scipy.special.erf(x)

def chidist(a,b):
	return 1 - scipy.stats.chi2.cdf(a,b)
	
	
def Monobit(log):
	s = 0
		
	for i in log:
		if i == 0:
			s+=1
		else:
			s-=1
	
	S = abs(s)/sqrt(len(log))
	
	P_value = cerf(S/sqrt(2))
	
	if P_value > 0.01:
		return  "random a sorozat"
	else:
		return  "fail"
		
def Blockbit(M,log):
	n = len(log)
	al = []
	N = int(n/M)-1

	for i in range(0,n,M):
		al.append( log[0+i:M+i].count(1)/float(M) )	
	khi_square = 4*M*sum([(a-0.5)**2 for a in al])
	P_value = chidist(khi_square,N)

	print P_value
	if P_value > 0.01:
		return  "random a sorozat"
	else:
		return "fail"
	
url = 'https://www.random.org/integers/?num=1000&min=0&max=1&col=1&base=10&format=plain&rnd=new'
log = urllib2.urlopen(url).readlines()

log = map(lambda k: int(k[0]), log)
freqs = Counter(log)

print freqs 
print Monobit(log) + '\n'

for i in [10,100,125,200]:
        print Blockbit(i,log) + '\n' + '-'*10
