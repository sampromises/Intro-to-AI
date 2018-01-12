''' 
Contains optimal (conflict-directed backjumping) solution.
'''

from copy import deepcopy
import sys

class BackjumpSolution:
 	def __init__(self, filepath):
		'''
		grid: contains initial values
		constr: list of ([(i1,j1), (i2,j2), ...], sum) constraints
		variables: list of [(i1,j1), (i2,j2), ...] modifiable positions
		domains: dict from (i,j) to [0,1,2...,9]
		mapping: dict from (i,j) to k, inverse lookup of variables[k]
		'''
		grid, constr, variables, domains, mapping = self.read_input(filepath)
		self.grid = grid
		self.constr = constr
		self.variables = variables
		self.domains = domains
		self.mapping = mapping

	def read_input(self, filepath):
		'''
		Read input into grid, constr, variables, and domains
		Each constraint is a tuple containing list of variables and desired sum
		'''
		grid = []
		constr = []
		variables = []
		domains = {}

		with open(filepath) as reader:
			size = int(reader.readline().rstrip())
			for i in xrange(size):
				vals = [int(x) for x in reader.readline().rstrip().split(' ')]
				grid.append(vals)
				for j in xrange(len(vals)):
					if vals[j] == -1:
						variables.append((i,j))
						domains[(i,j)] = range(10)

			row_sums = [int(x) for x in reader.readline().rstrip().split(' ')]
			for i in xrange(len(row_sums)):
				constr.append(([(i,j) for j in xrange(size)], row_sums[i]))

			col_sums = [int(x) for x in reader.readline().rstrip().split(' ')]
			for i in xrange(len(col_sums)):
				constr.append(([(j,i) for j in xrange(size)], col_sums[i]))

			diag_sums = [int(x) for x in reader.readline().rstrip().split(' ')]
			top_left = diag_sums[0]
			top_right = diag_sums[1]
			constr.append(([(i,i) for i in xrange(size)], top_left))
			constr.append(([(i, size - i - 1) for i in xrange(size)], 
							top_right))

		# Mapping maps tuples (i,j) to position in the variables list
		mapping = {}
		for i in xrange(len(variables)):
			mapping[variables[i]] = i

		return grid, constr, variables, domains, mapping

	def check_constr(self, grid):
		'''
		Given a grid and constraints, return False if we
		know a constraint will be violated (i.e. all squares
		in constraint are assigned and does not equal sum, 
		or running sum exceeds total)
		'''
		for nodes, total in self.constr:
			nodes_sum = 0
			found_empty = False # Did we find a un-filled square
			for (i,j) in nodes:
				if grid[i][j] == -1:
					found_empty = True
					continue
				nodes_sum += int(grid[i][j])
			if not found_empty and nodes_sum != int(total):
				return False
			elif nodes_sum > int(total):
				return False
		return True

	def solve(self):
		grid = deepcopy(self.grid)
		domains = deepcopy(self.domains)
		variables = deepcopy(self.variables)
		mapping = deepcopy(self.mapping)
		assignments = [-1 for i in xrange(len(variables))]
		conflicts = [[] for i in xrange(len(variables))]

		# If there are no variables, just check constraints
		if len(variables) == 0:
			if self.check_constr(grid):
				return self.print_result(grid)
			else:
				return self.print_result(None)

		curr_index = 0
		while(True):
			if curr_index >= len(variables):
				final_grid = self.fill_grid(grid, assignments, variables)
				return self.print_result(final_grid)
			if curr_index < 0:
				return self.print_result(None)

			(i, j) = variables[curr_index]
			if len(domains[(i,j)]) == 0:
				# Backtrack
				conflict_set = conflicts[curr_index]
				end_index = curr_index
				if len(conflict_set) == 0:
					curr_index -= 1
					start_index = curr_index
				else:
					# Update index to most recent element in conflcit set
					# Update conflict set of new index
					curr_index = max(conflict_set)
					start_index = curr_index
					curr_conflict = conflicts[curr_index]
					new_conflict = list(set().union(curr_conflict, conflict_set) - set([curr_index]))
					conflicts[curr_index] = new_conflict

				# Refresh assignments, domains, conflicts farther down the tree
				for k in xrange(curr_index + 1, len(assignments)):
					assignments[k] = -1
					var_i, var_j = variables[k]
					domains[(var_i, var_j)] = range(10)
					conflicts[k] = []
				if curr_index >= 0:
					next_i, next_j = variables[curr_index]
					domains[(next_i, next_j)].pop(0)
					assignments[curr_index] = -1 
				continue

			assignments[curr_index] = domains[(i,j)][0]
			tmp_grid = self.fill_grid(grid, assignments, variables)

			# Prune domains and add conflicts
			(check, prune_conflicts)= self.prune_domains(tmp_grid, 
				assignments, domains, conflicts, variables, mapping)
			if not check:
				if len(domains[(i,j)]) == 0:
					# Backtrack next loop
					continue
				domains[(i,j)].pop(0)
				curr_conflict = conflicts[curr_index]
				new_conflict = list(set().union(curr_conflict, prune_conflicts) - set([curr_index]))
				conflicts[curr_index] = new_conflict
				for k in xrange(curr_index + 1, len(assignments)):
					assignments[k] = -1
					var_i, var_j = variables[k]
					domains[(var_i, var_j)] = range(10)
					conflicts[k] = []
				assignments[curr_index] = -1
				continue

			# Check for any constraint violations
			if not self.check_constr(tmp_grid):
				if len(domains[(i,j)]) == 0:
					# Backtrack next loop
					continue
				domains[(i,j)].pop(0)
				for k in xrange(curr_index + 1, len(assignments)):
					assignments[k] = -1
					var_i, var_j = variables[k]
					domains[(var_i, var_j)] = range(10)
					conflicts[k] = []
				assignments[curr_index] = -1
				continue

			curr_index += 1

			variables, assignments = self.mrv(curr_index, variables, 
				assignments, domains, mapping, conflicts)

	def fill_grid(self, grid, assignments, variables):
		grid = deepcopy(grid)
		for k in xrange(len(variables)):
			(i,j) = variables[k]
			grid[i][j] = assignments[k]
		return grid

	def prune_domains(self, grid, assignments, domains, 
					  conflicts, variables, mapping):
		'''
		Loop through each constraint, and remove impossible domain values.
		Pruning needs to be done sufficiently well such that assigning any
		value from a domain will not lead to a violated constraint in the next 
		step. Whenever a domain is decreased, the conflict set is updated: add
		all assigned nodes from the constraint and then union with the conflict
		sets of the unassigned nodes.
		If we find that variable has an empty domain, return False and the
		conflict set of that variable.
		'''
		for nodes, total in self.constr:
			nodes_sum = 0
			found_empty = False
			empty_nodes = []
			for (i,j) in nodes:
				if grid[i][j] == -1:
					# Skip any constraints that are not all filled
					empty_nodes.append((i,j))
					continue
				nodes_sum += int(grid[i][j])

			if len(empty_nodes) == 1:
				# There can only be one value for this empty_node
				difference = total - nodes_sum
				empty_node = empty_nodes[0]
				old_domain = domains[empty_node]
				domain = [x for x in old_domain if x == difference]
				domains[empty_node] = domain
				if len(domain) < len(old_domain):
					# Check if pruned, then update conflict set
					empty_index = mapping[empty_node]
					for node in nodes:
						if node not in mapping:
							# Ignore non-variable nodes
							continue
						node_index = mapping[node]
						if (node_index != empty_index and node_index not in conflicts[empty_index] and 
							assignments[node_index] != -1):
							# Add other assigned nodes from the given constraint to conflict set
							conflicts[empty_index].append(node_index)
						elif node_index != empty_index:
							conflicts[empty_index] = list(set().union(conflicts[empty_index], conflicts[node_index]) - set([empty_index]))

			elif len(empty_nodes) > 1:
				for empty_node in empty_nodes:
					# Domain values cannot be too big
					old_domain = domains[empty_node]
					min_total = nodes_sum
					for other_node in empty_nodes:
						if empty_node == other_node:
							continue
						if len(domains[other_node]) == 0:
							# Found an empty domain, exit early
							continue
						min_total += min(domains[other_node])
					upper_bound = total - min_total

					domain = [x for x in old_domain if x <= upper_bound]

					# Domain values cannot be too small
					max_total = nodes_sum
					for other_node in empty_nodes:
						if empty_node == other_node:
							continue
						if len(domains[other_node]) == 0:
							continue
						max_total += max(domains[other_node])
					lower_bound = total - max_total
					if lower_bound >= 0:
						domain = [x for x in domain if x >= lower_bound]

					domains[empty_node] = domain
					if len(domain) < len(old_domain):
						# Update conflict set, since domain was pruned
						empty_index = mapping[empty_node]

						for node in nodes:
							if node not in mapping:
								# Ignore non-variable nodes
								continue
							node_index = mapping[node]
							if (node_index != empty_index and 
								node_index not in conflicts[empty_index] and 
								assignments[node_index] != -1):
								conflicts[empty_index].append(node_index)
							elif node_index != empty_index:
								conflicts[empty_index] = list(set().union(conflicts[empty_index], conflicts[node_index]) - set([empty_index]))

		# Return False if any domains are empty
		for k in xrange(len(variables)):
			(i,j) = variables[k]
			domain = domains[(i,j)]
			if len(domain) == 0:
				return (False, conflicts[k])
		return (True, None)

	def mrv(self, index, variables, assignments, domains, mapping, conflicts):
		'''
		Return a new copy of both variables and assignments such that
		variables[index] contains the variable with the min number of
		remaining values. Swap other data structures as necessary. 
		'''
		variables = deepcopy(variables)
		assignments = deepcopy(assignments)

		minIndex = None
		minValue = None
		for i in xrange(index, index + len(variables[index:])):
			if i == index and assignments[i] != -1:
				# Index position is an assigned variable
				return (variables, assignments)
			elif assignments[i] != -1:
				continue
			elif minIndex is None:
				minIndex = i
				minValue = len(domains[variables[i]])
			elif len(domains[variables[i]]) < minValue:
				minIndex = i
				minValue = len(domains[variables[i]])

		if minIndex is None:
			return (variables, assignments)

		# Swap current variable with minimum variable (move to 'front')
		# Update variables, mapping, conflicts, assignments
		tmp = variables[index]
		variables[index] = variables[minIndex]
		variables[minIndex] = tmp

		mapping[variables[index]] = index
		mapping[variables[minIndex]] = minIndex

		tmp = deepcopy(conflicts[index])
		conflicts[index] = deepcopy(conflicts[minIndex])
		conflicts[minIndex] = tmp

		tmp = assignments[index]
		assignments[index] = assignments[minIndex]
		assignments[minIndex] = tmp

		return (variables, assignments)

	def print_result(self, grid):
		if grid is None:
			print 'False'
		else:
			print 'True'
			for i in xrange(len(grid)):
				grid_str = [str(x) for x in grid[i]]
				print ' '.join(grid_str)

if __name__ == '__main__':
	filename = sys.argv[1]
	m2 = BackjumpSolution(filename)
	m2.solve()