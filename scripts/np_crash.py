import numpy as np

def runs_fine():
    data = np.random.rand(3000, 121, 20, 6)
    print "Array created;", data.shape
    data = 3 * data + 10
    print "scaled to", data.min(), data.max()
    return data

def causes_segfault():
    data = np.random.rand(5000, 121, 20, 6)
    print "Array created;", data.shape
    data = 3 * data + 10
    print "scaled to", data.min(), data.max()
    return data

if __name__ == '__main__':
    runs_fine()
    print
    causes_segfault()
