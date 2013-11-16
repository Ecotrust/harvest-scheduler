# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from collections import defaultdict
import itertools

xs = defaultdict(list)
ys = defaultdict(list)
steps = []
temps = []
with open("./test_out.csv",'r') as fh:
    for line in fh:
        step, cost = [float(x) for x in line.split(",")[:2]]
        stype = line.split(",")[2]
        xs[stype].append(step) 
        ys[stype].append(cost)
        steps.append(int(line.split(",")[0]))
        temps.append(float(line.split(",")[3]))

import matplotlib.pylab as pylab
pylab.rcParams['figure.figsize'] = 16, 12 

fig, axes = plt.subplots(nrows=1, ncols=1)

colors = itertools.cycle(["yellow", "blue", "green", "black"])
for key in ["reject", "accept", "accept_improve", "new best"]:
    x = xs[key]
    y = ys[key]
    #plt.figsize(14,8)
    if key == "new best":
        alpha = 1.0
        size = 24
        plt.plot(x, y, color="grey")
    else:
        alpha = 0.3
        size = 12
    plt.scatter(x, y, label=key, s=size, color=colors.next(), alpha=alpha)
    plt.legend()
    #axes[0].scatter(x, y, label=key, s=size, color=colors.next(), alpha=alpha)
    #axes[0].legend()
    
#axes[1].plot(steps, temps)
#axes[1].set_xlim(axes[0].get_xlim())

plt.title('Simulated annealing')
plt.xlabel('step')
plt.ylabel('objective function')

plt.show()
#plt.savefig("test.png")
