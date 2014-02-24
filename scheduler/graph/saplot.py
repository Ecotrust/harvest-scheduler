from pylab import plt
from collections import deque

class AnalogPlot:
    def __init__(self, width):
        # set plot to animated
        self.x1s = [0]
        self.y1s = [0]
        self.x2s = [0]
        self.y2s = [0]
        self.x3s = [0]
        self.y3s = [0]
        self.plt1, self.plt2, self.plt3 = plt.plot(
            self.x1s, self.y1s, 'rx',
            self.x2s, self.y2s, 'b.',
            self.x3s, self.y3s, 'gs',
            alpha=0.05, linewidth=3)
        self.latest = deque([0] * 20)
        self.plt3.set_alpha = 0.8
        plt.ylim([0, 100])
        plt.xlim([0, width])
        plt.ion()


    # update plot
    def append(self, plot_cache):
        newpoints = [x[0] for x in plot_cache]
        self.latest.popleft()
        self.latest.popleft()
        self.latest.append(max(newpoints))
        self.latest.append(min(newpoints))

        for point, step, mtype, best_metric in plot_cache:
            if mtype in ('accept', 'acceptimprove'):
                self.y2s.append(point)
                self.x2s.append(step)
            elif mtype == "newbest":
                self.y3s.append(point)
                self.x3s.append(step)
            else:
                self.y1s.append(point)
                self.x1s.append(step)

        self.plt1.set_xdata(self.x1s)
        self.plt1.set_ydata(self.y1s)
        self.plt2.set_xdata(self.x2s)
        self.plt2.set_ydata(self.y2s)
        self.plt3.set_xdata(self.x3s)
        self.plt3.set_ydata(self.y3s)
        # import ipdb; ipdb.set_trace()
        plt.ylim([min(self.latest)*0.9, max(self.latest)])
        plt.draw()