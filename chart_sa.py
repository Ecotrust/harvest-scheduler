# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from collections import defaultdict
import itertools

from mpltools import style
#style.use('ggplot')
style.use('grayscale')

xs = defaultdict(list)
ys = defaultdict(list)
steps = []
temps = []
with open("./__schedule.log",'r') as fh:
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

colors = itertools.cycle(["#D95F02", "#1B9E77", "#7570B3", "#E7298A"])
for key in ["reject", "accept", "accept+improve", "new best"]:
    x = xs[key]
    y = ys[key]
    #plt.figsize(14,8)
    if key == "new best":
        alpha = 1.0
        size = 20
        #plt.plot(x, y, "-", alpha=0.5, color="grey")
    else:
        alpha = 0.4
        size = 16
    plt.scatter(x, y, label=key, s=size, alpha=alpha, color=colors.next())
    plt.legend()
    #axes[0].scatter(x, y, label=key, s=size, color=colors.next(), alpha=alpha)
    #axes[0].legend()
    
#axes[1].plot(steps, temps)
#axes[1].set_xlim(axes[0].get_xlim())

max_step = max(steps)
buff = max_step / 100.0
plt.xlim(0 - buff, max_step + buff)
plt.title('Simulated annealing')
plt.xlabel('step')
plt.ylabel('objective function')

plt.show()
#plt.savefig("test.png")
