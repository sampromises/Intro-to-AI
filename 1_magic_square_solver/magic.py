'''
Author: Sam Kim

=========================== NxN MAGIC SQUARE SOLVER ===========================
This is an implementation of an iterative backtracking algorithm that finds a 
solution for a NxN magic square, which is an incomplete grid with sum 
constraints for the rows, columns, and 2 diagonals.

The domains are pruned once in the beginning and pruned again every time a new
value is placed on the grid or a value is removed from the grid (backtracked).
The domain pruning works in 2 sequential stages:
    1) Prune the domains based on the sum/col/diag constraints
    2) Prune the domains based on the lower/upper bounds of other variables

For backtracking, a list of variables is kept, which is sorted according to
two most-constraining heuristics:
    1) From the smallest domains to the largest
    2) Highest total of other variables in same row/col/diag to lowest

From the beginning, the variables are sorted from most to least constrained,
    [X0, X1, X2, .... , Xn]
      ^
with a variable pointer to the current variable being working on.

Each value is popped off current variable domain (which is well-pruned). Each
value is tried on the grid and if it doesn't break constraints: (1) the 
variables are RE-SORTED and (2) the domains are RE-PRUNED from i+1 and onward.
Finally, the variable pointer is incremented to work on the next variable,
    [X0, X1', X2', .... , Xn']
          ^

If the domain is flushed and a good value wasn't found for the variable, then
the variable pointer is decremented, the previous value is removed because it
led to a bad path and, again, (1) the variables are RE-SORTED and (2) the
domains are RE-PRUNED from i + 1 and onward,
    [X0, X1'', X2'', .... , Xn'']
      ^

Success is returned whenever a complete grid is created that satisfies all 
constraints.

Failure is returned in 2 cases:
  1) Backtracking reaches back to the first variable and the domain is empty.
  2) Forwarding reaches the last variable and the domain is flushed out.
===============================================================================

-------------------------------------------------------------------------------
Specs: given a file like below, find a magic square with non-neg numbers
First line is dimension (n) of square
Next d lines contain the grid. -1 is placeholder for empty, modifiable value
Next line contains n row sums (first number is sum of top row)
Next line contains n col sums (first number is sum of leftmost col)
Next line contains 2 diag sums (first number is top-left to bottom-right)
-------------------------------------------------------------------------------
3         <- dimension (n) of square
-1 -1 0   <- grid row 0
5 -1 2    <- grid row 1
-1 -1 -1  <- grid row 2 = n-1
10 8 9    <- n row sums (top to bottom)
12 10 5   <- n col sums (left to right)
9 3       <- diag sums (left, right)
-------------------------------------------------------------------------------
From the above input, the following would be appropriate output (stdout) 
-------------------------------------------------------------------------------
True
5 5 0
5 1 2
2 4 3
-------------------------------------------------------------------------------
'''

import sys

D_MIN = 0
D_MAX = 9

# Given a grid and constraints, returns True if the grid is consistent with 
# its constraints; False otherwise
# We check the following constraints:
#   - the sum of a row/col/diag <= the row/col/diag constraint
#   - any free variable must have a nonempty domain
#   - if the board is filled, it must be complete
def is_consistent(grid, constraints):
    n = len(grid)

    # Check the row/col/diag sum constraints
    row_constraints = constraints[0]
    col_constraints = constraints[1]
    diag_constraints = constraints[2]

    # Check if board is filled, then it must be complete as well
    free_vars = 0
    for row in grid: free_vars += row.count(-1)
    if free_vars == 0: return is_complete(grid, constraints)

    row_sums = [0] * n
    col_sums = [0] * n
    diag_sums = [0, 0]
    for r in xrange(n):
        for c in xrange(n):
            value = grid[r][c]
            if value != -1:
                row_sums[r] += value
                col_sums[c] += value

                if (r == c): diag_sums[0] += value
                if (r == n-1-c): diag_sums[1] += value

    for i in xrange(n):
        if row_sums[i] > row_constraints[i]: return False
        if col_sums[i] > col_constraints[i]: return False

    if diag_sums[0] > diag_constraints[0]: return False
    if diag_sums[1] > diag_constraints[1]: return False

    return True


# Given a grid and constraints, returns True if the grid is filled and fulfills
# the constraints. Returns false otherwise (not filled or violates constraints)
def is_complete(grid, constraints):
    n = len(grid)

    # Check the row/col/diag sum constraints
    row_constraints = constraints[0]
    col_constraints = constraints[1]
    diag_constraints = constraints[2]

    row_sums = [0] * n
    col_sums = [0] * n
    diag_sums = [0, 0]
    for r in xrange(n):
        for c in xrange(n):
            value = grid[r][c]
            if value == -1:
                # Board must be full
                return False
            else:
                row_sums[r] += value
                col_sums[c] += value

                if (r == c): diag_sums[0] += value
                if (r == n-1-c): diag_sums[1] += value

    for i in xrange(n):
        if row_sums[i] != row_constraints[i]: return False
        if col_sums[i] != col_constraints[i]: return False

    if diag_sums[0] != diag_constraints[0]: return False
    if diag_sums[1] != diag_constraints[1]: return False

    return True


# PRUNE THE DOMAINS BASED ON INITIAL SUM CONSTRAINTS
# get_domains() takes in a grid and constraints and outputs an (n x n) array
# that replaces each value with a list of each value's domain (valid inputs).
# If the list is empty, it means the value is fixed.
#
# We do this by doing the following for each value at grid[r][c]...
#
# To find the upper bound for grid[r][c], we compute:
#     r_upper = r_constraints - r_fixed_sum
#     c_upper = c_constraints - c_fixed_sum
#     d0_upper = d0_constraints - d0_fixed_sum
#     d1_upper = d1_constraints - d1_fixed_sum
#     upper = min(9, r_upper, c_upper, d0_upper, d1_upper)
#
# To find the lower bound for grid[r][c], we assume that other free variables
# are assigned the most they can possibly be (9) and compute:
#     r_lower = r_constraints - r_fixed_sum - (9 * r_free_count) + 9
#     c_lower = c_constraints - c_fixed_sum - (9 * c_free_count) + 9
#     d0_lower = d0_constraints - d0_fixed_sum - (9 * d0_free_count) + 9
#     d1_lower = d1_constraints - d1_fixed_sum - (9 * d1_free_count) + 9
#     lower = max(0, r_upper, c_upper, d0_upper, d1_upper)
#
def prune_domains_sums(grid, constraints):
    n = len(grid)
    result = [ [[] for c in xrange(n)] for r in xrange(n) ]

    # Parse the row, col, diag sum constraints
    row_constraints = constraints[0]
    col_constraints = constraints[1]
    diag_constraints = constraints[2]

    # Build sum of fixed variables and count number of free variables
    row_fixed_sums = [0 for i in xrange(n)]
    col_fixed_sums = [0 for i in xrange(n)]
    diag_fixed_sums = [0, 0]
    row_free_counts = [0 for i in xrange(n)]
    col_free_counts = [0 for i in xrange(n)]
    diag_free_counts = [0, 0]
    for r in xrange(n):
        for c in xrange(n):
            grid_val = grid[r][c]
            # Fixed values
            if (grid_val != -1):
                row_fixed_sums[r] += grid_val
                col_fixed_sums[c] += grid_val

                if (r == c): diag_fixed_sums[0] += grid_val
                if (r == n-1-c): diag_fixed_sums[1] += grid_val
            # Free values
            else:
                row_free_counts[r] += 1
                col_free_counts[c] += 1

                if (r == c): diag_free_counts[0] += 1
                if (r == n-1-c): diag_free_counts[1] += 1

    # Compute the domains for each elem at grid[r][c] by finding
    # an upper and lower bound for each mutable value
    for r in xrange(n):
        for c in xrange(n):
            if (grid[r][c] == -1):
                row_hi =  row_constraints[r] - row_fixed_sums[r]
                col_hi =  col_constraints[c] - col_fixed_sums[c]
                # Need to add 9 to ignore self in calculation
                row_lo =  row_hi - D_MAX * (row_free_counts[r]-1)
                col_lo =  col_hi -  D_MAX * (col_free_counts[c]-1)

                # Setting defaults for non-diagonals
                diag0_hi = diag1_hi = D_MAX
                diag0_lo = diag1_lo = D_MIN
                if (r == c):
                    diag0_hi = diag_constraints[0] - diag_fixed_sums[0]
                    diag0_lo = diag0_hi - D_MAX * (diag_free_counts[0]-1)
                if (r == n-1-c):
                    diag1_hi = diag_constraints[1] - diag_fixed_sums[1]
                    diag1_lo = diag1_hi - D_MAX * (diag_free_counts[1]-1)
                hi = min(D_MAX, row_hi, col_hi, diag0_hi, diag1_hi)
                lo = max(D_MIN, row_lo, col_lo, diag0_lo, diag1_lo)

                result[r][c] = range(lo, hi + 1)

    return result

# PRUNE THE DOMAINS FURTHER, BASED ON OTHER DOMAIN CONSTRAINTS.
# The idea is:
#   new_lower = constraint - BEST_of_other_variables
#   new_upper = constraint - WORST_of_other_variables
def prune_domains_cross(grid, constraints):
    n = len(grid)
    
    # Parse the row, col, diag sum constraints
    row_constraints = constraints[0]
    col_constraints = constraints[1]
    diag_constraints = constraints[2]

    domains = prune_domains_sums(grid, constraints)

    row_max_sums = [0] * n
    row_min_sums = [0] * n
    col_max_sums = [0] * n
    col_min_sums = [0] * n
    diag_max_sums = [0, 0]
    diag_min_sums = [0, 0]

    # Get the BEST and WORST that the variables can do for each row, col, diag
    for r in xrange(n):
        for c in xrange(n):
            if grid[r][c] == -1:
                if domains[r][c] != []:

                    row_max_sums[r] += max(domains[r][c])
                    row_min_sums[r] += min(domains[r][c])
                    col_max_sums[c] += max(domains[r][c])
                    col_min_sums[c] += min(domains[r][c])

                    if (r == c):
                        diag_max_sums[0] += max(domains[r][c])
                        diag_min_sums[0] += min(domains[r][c])

                    if (r == n-1-c):
                        diag_max_sums[1] += max(domains[r][c])
                        diag_min_sums[1] += min(domains[r][c])
            else:
                row_max_sums[r] += grid[r][c]
                row_min_sums[r] += grid[r][c]
                col_max_sums[c] += grid[r][c]
                col_min_sums[c] += grid[r][c]

                if (r == c):
                    diag_max_sums[0] += grid[r][c]
                    diag_min_sums[0] += grid[r][c]

                if (r == n-1-c):
                    diag_max_sums[1] += grid[r][c]
                    diag_min_sums[1] += grid[r][c]

    # Now, create the new domains list to return
    new_domains = [ [[] for c in xrange(n)] for r in xrange(n) ]

    for r in xrange(n):
        for c in xrange(n):
            if grid[r][c] == -1:
                if domains[r][c] != []:
                    new_row_min = (row_constraints[r] - 
                                   (row_max_sums[r] - max(domains[r][c])) )
                    new_row_max = (row_constraints[r] -
                                   (row_min_sums[r] - min(domains[r][c])))

                    new_col_min = (col_constraints[c] -
                                   (col_max_sums[c] - max(domains[r][c])))
                    new_col_max = (col_constraints[c] -
                                   (col_min_sums[c] - min(domains[r][c])))

                    # Setting defaults for non-diagonals
                    new_diag0_min = new_diag1_min = D_MIN
                    new_diag0_max = new_diag1_max = D_MAX
                    if (r == c):
                        new_diag0_min = (diag_constraints[0] -
                                       (diag_max_sums[0] - max(domains[r][c])) )
                        new_diag0_max = (diag_constraints[0] -
                                       (diag_min_sums[0] - min(domains[r][c])) )
                    if (r == n-1-c):
                        new_diag1_min = (diag_constraints[1] -
                                       (diag_max_sums[1] - max(domains[r][c])) )
                        new_diag1_max = (diag_constraints[1] -
                                       (diag_min_sums[1] - min(domains[r][c])) )
                else:
                    new_row_max=new_col_max=new_diag0_max=new_diag1_max=D_MAX
                    new_row_min=new_col_min=new_diag0_min=new_diag1_min=D_MIN


                new_max = min(D_MAX, new_row_max, new_col_max,
                              new_diag0_max, new_diag1_max)
                new_min = max(D_MIN, new_row_min, new_col_min,
                              new_diag0_min, new_diag1_min)

                new_domain = range(new_min, new_max + 1)
                old_domain = domains[r][c]

                # Only assign the new domain if it's both VALID and
                # BETTER than the old one
                if len(new_domain) < len(old_domain) and new_domain != []:
                    new_domains[r][c] = new_domain
                else:
                    new_domains[r][c] = old_domain

    return new_domains

# Wrapper function to get domains as a 3D list, where each entry of the NxN
# is the domain for that (r, c)
def get_domains(grid, constraints):
    return prune_domains_cross(grid, constraints)

# MOST CONSTRAINED VARIABLE
# 1) Sort from smallest to largest domain length
# 2) For ties, then sort by count of other free variables in same row/col/diag
def var_sort_fn(A, B):
    (Ar, Ac, Ad, Aw) = A
    (Br, Bc, Bd, Bw) = B

    if len(Ad) < len(Bd):
        return -1
    elif len(Ad) > len(Bd):
        return 1
    else:
        if Aw < Bw:
            return 1 # Surprisingly, MORE free variables is better
        else:
            return -1

# Given a grid and constraints, return an array of [r, c, domain] lists that
# is sorted from most to least constrained.
def get_vars_and_domains(grid, constraints):
    n = len(grid)
    domains = get_domains(grid, constraints)
    result = []

    for r in xrange(n):
        for c in xrange(n):
            # Only concerned with mutable variables
            if (grid[r][c] == -1):
                # Append a triplet of (row, col, domain)
                result.append( [r, c, domains[r][c]] )

    # Heuristic: count other free variables in row/col/diag
    row_free_counts = [0 for i in xrange(n)]
    col_free_counts = [0 for i in xrange(n)]
    diag_free_counts = [0, 0]

    for r in xrange(n):
        for c in xrange(n):
            # Count all the free variables
            if (grid[r][c] == -1):
                row_free_counts[r] += 1
                col_free_counts[c] += 1

                if (r == c): diag_free_counts[0] += 1
                if (r == n-1-c): diag_free_counts[1] += 1

    # Add 'weight' to each variable, so sort function can use it
    for var in result:
        (r, c, domain) = var

        other_count = row_free_counts[r] + col_free_counts[c]
        if (r == c): other_count += diag_free_counts[0]
        if (r == n-1-c): other_count += diag_free_counts[1]
        var.append(other_count) # variable packed as: [r, c, domain, weight]

    # Return the list, sorted by most to least constrained
    return sorted(result, var_sort_fn)

# Takes in the grid, constraints to update:
#   1) The ORDER of the variables, from most constrained to least constrained
#   2) The new domains for the i+1 variable and onward
def update_vars_and_domains(grid, constraints, curr_var, variables):
    n = len(grid)
    # Latest, best sorted vars/domains
    new_variables = get_vars_and_domains(grid, constraints)
    keep_list = []
    remove_list = []

    # Want to keep the exact same [0:i] variables
    for i in xrange(curr_var + 1):
        # Make list to keep old ones
        keep_list.append(variables[i])

        # Update new_variables to remove new ones
        (old_r, old_c, old_d, old_w) = variables[i]
        for new_var in new_variables:
            (new_r, new_c, new_d, new_w) = new_var
            if (new_r, new_c) == (old_r, old_c):
                # Don't want to update this, remove this
                remove_list.append(new_var)

    len_new_var_pre = len(new_variables)

    # Make the removals
    for bad_var in remove_list:
        new_variables.remove(bad_var)

    result = keep_list + new_variables

    return result

def solve(grid, constraints):
    # Edge case?
    if is_complete(grid, constraints): return grid

    # Get possible variables and domains, [ (r,c,d,w) ... ]
    variables = get_vars_and_domains(grid, constraints)
    # Index pointer to the variable we're working with
    curr_var = 0

    while curr_var < len(variables):
        # Go through all the variables
        (r, c, domain, w) = variables[curr_var]
        value_placed = False

        while domain != [] and grid[r][c] == -1:
            # Pop a value off the domain to try
            value = domain.pop(0)
            grid[r][c] = value

            if is_complete(grid, constraints):
                # Woo hoo!
                return grid
            elif is_consistent(grid, constraints):
                # Prune domains further with value placed
                prev_var_length = len(variables)
                variables = update_vars_and_domains(grid, constraints,
                                                    curr_var, variables)
                value_placed = True
                curr_var += 1
                break
            else:
                # Bad value, remove it
                grid[r][c] = -1

        if not value_placed:
            # Reached end of domain and we didn't find a good value

            # Can't backtrack anymore -> FAILURE
            if (curr_var == 0 and domain == []):
                return None

            # Backtrack: Remove previous variable's value and reset domains
            curr_var -= 1
            (r, c, domain, w) = variables[curr_var]
            grid[r][c] = -1
            variables = update_vars_and_domains(grid, constraints,
                                                curr_var, variables)

    # Reached end of variables, no solution found
    return None

'''
read_input takes in a command line path to the sample text file, outlined 
above.
It will return the solution grid if one is found and return None otherwise.
'''
def read_input(path):
    input_grid = []
    with open(path) as reader:
        size = int(reader.readline().rstrip())

        for i in xrange(size):
            vals = [int(x) for x in reader.readline().rstrip().split(' ')]
            input_grid.append(vals)

        # Do stuff with these
        row_sums = [int(x) for x in reader.readline().rstrip().split(' ')]
        col_sums = [int(x) for x in reader.readline().rstrip().split(' ')]
        diag_sums = [int(x) for x in reader.readline().rstrip().split(' ')]

    constraints = [row_sums, col_sums, diag_sums]

    return (input_grid, constraints)

def print_result(grid):
    if grid is None:
        print 'False'
    else:
        print 'True'
        for i in xrange(len(grid)):
            grid_str = [str(x) for x in grid[i]]
            print ' '.join(grid_str)

if __name__ == '__main__':
    if (len(sys.argv) > 1):
        filename = sys.argv[1]
        (input_grid, constraints) = read_input(filename)
        grid = solve(input_grid, constraints)
        print_result(grid)