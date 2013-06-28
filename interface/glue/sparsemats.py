from collections import defaultdict

__author__ = 'Faisal'

class Sparse2DMat(object):
    def __init__(self, rows=0, cols=0, default=0):
        self.mat = {}
        self.rows = int(rows)
        self.cols = int(cols)
        self.default = default

    def __setitem__(self, (i, j), val):
        self.mat[int(i), int(j)] = val
        if int(i) + 1 > self.rows: self.rows = int(i) + 1
        if int(j) + 1 > self.cols: self.cols = int(j) + 1

    def __getitem__(self, (i, j)):
        if (int(i),int(j)) not in self.mat:
            return self.default

        return self.mat[int(i), int(j)]

    def row(self, i):
        return [self.mat.get((int(i),x),0) for x in range(0, self.cols)]

    def col(self, j):
        return [self.mat.get((x,int(j)),0) for x in range(0, self.rows)]

    def tolist(self):
        rows = []
        for i in range(0, self.rows):
            cols = []
            for j in range(0, self.cols):
                if (i, j) in self.mat:
                    cols.append(self.mat[i, j])
                else:
                    cols.append(self.default)
            rows.append(cols)
        return rows

    def tonative(self):
        listified = self.tolist()
        return "[%s]" % " ; ".join([" ".join([str(c) for c in row]) for row in listified])
