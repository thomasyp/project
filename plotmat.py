import numpy as np 
import matplotlib.pyplot as plt
from scipy.integrate import quad,dblquad,nquad



x = []
d = 1e-9
for ii in range(345):
    
    x.append(d)
    d = d * 1.0715193

a1 = 0.965
b1 = 2.29
c1 = 0.4527046265529567
xarr1 = np.array(x)
yarr1 = c1 * np.exp(-1*xarr1/a1) * np.sinh((b1*xarr1)**0.5)

a2 = 0.88111
b2 = 3.4005
c2 = 0.3498070938594154
xarr2 = np.array(x)
yarr2 = c2 * np.exp(-1*xarr2/a2) * np.sinh((b2*xarr2)**0.5)
plt.plot(xarr1, yarr1, xarr2, yarr2)

plt.xlabel('decreasing time (s)')
plt.ylabel('$E  \ (MeV) $')

plt.xscale('log')
plt.ylim(0, 0.4)
plt.xlim(1e-6, 10)
plt.grid(True)

plt.show()

#print(quad(lambda x:np.exp(-x/a2)*np.sinh((b2*x)**0.5),0,np.inf))