'''
Create randomized test cases
'''
from random import randint
import sys
import math

def generate(n, neg_count=None, neg_fn = None):
    print n
    grid = [[0]*n for _ in xrange(n)]
    for i in xrange(n):
        for j in xrange(n):
            grid[i][j] = randint(0,9)
    
    row_sums = []
    for i in xrange(n):
        row_sums.append(sum(grid[i]))
    row_str = [str(x) for x in row_sums]

    col_sums = [0]*n
    for i in xrange(n):
        for j in xrange(n):
            col_sums[j] += grid[i][j]
    col_str = [str(x) for x in col_sums]

    diag_sums = [0,0]
    for i in xrange(n):
        diag_sums[0] += grid[i][i]
        diag_sums[1] += grid[i][n-i-1]
    diag_str = [str(x) for x in diag_sums]

    if neg_fn is not None and neg_count is not None:
        neg_fn(grid, neg_count)

    for i in xrange(n):
        grid_str = [str(x) for x in grid[i]]
        print ' '.join(grid_str)

    print ' '.join(row_str)
    print ' '.join(col_str)
    print ' '.join(diag_str)

def rand_neg(grid, neg_count):
    for k in xrange(neg_count):
        i = randint(0,len(grid)-1)
        j = randint(0, len(grid)-1)
        grid[i][j] = -1
    


if __name__ == '__main__':
    count = int(sys.argv[1])
    neg_count = int(sys.argv[2])
    generate(count, neg_count, rand_neg)
