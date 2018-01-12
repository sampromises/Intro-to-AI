# Checks if the magic square is completed correctly.
# The first command line argument should be the path to test case file.
# The second command line argument should be the path to completed square file.
# The third command line argument should be a boolean denoting whether if there exists a valid solution.

import sys

def check(input_file_path, output_file_path, isValid):
	size = -1
	input_grid = []
	row_sums = []
	col_sums = []
	diag_sums = []

	with open(input_file_path) as input:
		size = int(input.readline().rstrip())

		for i in xrange(size):
			vals = [int(x) for x in input.readline().rstrip().split(' ')]
			input_grid.append(vals)

		row_sums = [int(x) for x in input.readline().rstrip().split(' ')]
		col_sums = [int(x) for x in input.readline().rstrip().split(' ')]
		diag_sums = [int(x) for x in input.readline().rstrip().split(' ')]

	output_grid = []

	with open(output_file_path) as output:
		output_isValid = output.readline().rstrip()
		if output_isValid != isValid:
			return False
		if output_isValid == 'False':
			return True
		for i in xrange(size):
			vals = [int(x) for x in output.readline().rstrip().split(' ')]
			if len(vals) != size:
				return False
			output_grid.append(vals)

	# check if output does not contradict input values, and is in range [0,9]
	for i in xrange(size):
		for j in xrange(size):
			input_val = input_grid[i][j]
			output_val = output_grid[i][j]
			if (input_val != -1) and (input_val != output_val):
				return False
			if (output_val < 0) or (output_val > 9):
				return False

	# check for row sums
	for i in xrange(size):
		row_sum = 0
		for j in xrange(size):
			row_sum += output_grid[i][j]
		if row_sum != row_sums[i]:
			return False

	# check for column sums
	for j in xrange(size):
		col_sum = 0
		for i in xrange(size):
			col_sum += output_grid[i][j]
		if col_sum != col_sums[j]:
			return False

	# check for first diagonal sum
	diag_sum = 0
	for i in xrange(size):
		diag_sum += output_grid[i][i]
	if diag_sum != diag_sums[0]:
		return False

	# check for second diagonal sum
	diag_sum = 0
	for i in xrange(size):
		diag_sum += output_grid[i][size-1-i]
	if diag_sum != diag_sums[1]:
		return False

	return True

input_file_path = sys.argv[1]
output_file_path = sys.argv[2]
isValid = sys.argv[3]
print check(input_file_path, output_file_path, isValid)