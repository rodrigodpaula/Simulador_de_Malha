import os
import numpy as np
from scipy import stats
from abc import ABCMeta, abstractmethod


class BlockTime:
    __metaclass__ = ABCMeta

    def __init__(self, data_folder):
        self.data_folder = data_folder

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def get_block(self, fr, to):
        pass


class Kernel(BlockTime):
    def __init__(self, data_folder):
        super(Kernel, self).__init__(data_folder)
        self.kdes = {}

    def init(self):
        for fname in os.listdir(self.data_folder):
            path = '%s/%s' % (self.data_folder, fname)
            x = np.fromfile(path, dtype=float, sep='\n')
            pair = fname.split('_')
            key = '%s%s' % (pair[0], pair[1])
            if len(x) > 1:
                try:
                    self.kdes[key] = stats.gaussian_kde(x)
                except:
                    print 'KDE ERROR %s %s' % (pair[0], pair[1])

    def get_block(self, fr, to):
        key = '%s%s' % (fr, to)
        return self.kdes[key].resample(1)[0][0] if key in self.kdes else None


class Percentile(BlockTime):
    def __init__(self, data_folder, percentile=50):
        super(Percentile, self).__init__(data_folder)
        self.percentile = percentile
        self.data = {}

    def init(self):
        for fname in os.listdir(self.data_folder):
            path = '%s/%s' % (self.data_folder, fname)
            x = np.fromfile(path, dtype=float, sep='\n')
            pair = fname.split('_')
            key = '%s%s' % (pair[0], pair[1])
            self.data[key] = x

    def get_block(self, fr, to):
        key = '%s%s' % (fr, to)
        try:
            return np.percentile(self.data[key], self.percentile) if key in self.data else None
        except:
            return None
