import matplotlib.pyplot as plt
import numpy as np


l = np.array([[10, 20.416, 3.347],
[50, 18.58, 1.564],
[100, 20.205, 1.64],
[200, 29.38, 1.513],
[500, 23.179, 1.027],
[1000, 22.347, 0.902],
[2000, 20.827, 0.868],
[5000, 21.403, 0.828],
[10000, 26.912, 1.115]])

g = np.array([[10, 24.484, 7.501],
[50, 9.224, 3.357],
[100, 8.382, 3.242],
[200, 8.156, 3.048],
[500, 7.019, 2.913],
[1000, 7.062, 3.089],
[2000, 6.626, 2.911],
[5000, 5.86, 2.655],
[10000, 5.652, 2.594]])

lg = np.array([[10, 16.149, 3.087],
[50, 13.79, 2.172],
[100, 15.624, 1.88],
[200, 13.135, 1.232],
[500, 13.171, 0.965],
[1000, 12.582, 0.932],
[2000, 12.14, 0.879],
[5000, 12.049, 0.726],
[10000, 11.774, 0.773]])

il = np.array([[10, 11.274, 3.016],
[50, 11.2, 1.392],
[100, 11.883, 1.121],
[200, 12.234, 0.871],
[500, 11.626, 0.652],
[1000, 12.22, 0.667],
[2000, 12.263, 0.71],
[5000, 13.131, 0.689],
[10000, 11.912, 0.665]])




plt.title("Average Time Steps vs Training Iterations")
axes = plt.gca()
axes.set_xlim([int(np.log(10)),int(np.log(10000))])
# axes.set_ylim([0,])
plt.xlabel("Training Iterations (ln)")
plt.ylabel("Average Time Steps");
plt.plot(np.log(l[:,0]), l[:,1], label='Local')
plt.plot(np.log(g[:,0]), g[:,1], label='Global')
plt.plot(np.log(lg[:,0]), lg[:,1], label='Local-Global')
plt.plot(np.log(il[:,0]), il[:,1], label='Improved-Local')
plt.legend(loc='best')
plt.show()

plt.title("Average Amount of Accidents vs Training Iterations")
axes = plt.gca()
axes.set_xlim([int(np.log(10)),int(np.log(10000))])
# axes.set_ylim([0,])
plt.xlabel("Training Iterations (ln)")
plt.ylabel("Average Amount of Accidents");
plt.plot(np.log(l[:,0]), l[:,2], label='Local')
plt.plot(np.log(g[:,0]), g[:,2], label='Global')
plt.plot(np.log(lg[:,0]), lg[:,2], label='Local-Global')
plt.plot(np.log(il[:,0]), il[:,2], label='Improved-Local')
plt.legend(loc='best')
plt.show()