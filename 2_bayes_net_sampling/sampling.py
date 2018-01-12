'''
Author: Sam Kim

An exercise in bayes net sampling methods by implementing direct, rejection,
likelihood, and Gibbs sampling.

'''

import sys, random

random.seed(10000) # Use this seed (10000) when submitting to autolab

DEBUG = 0

class BayesNet:
    """
    variables: dictionary mapping letter (ex: 'A') to a Variable object
    letters: list of letters in topological order
    query: Query object representing the query variable and evidence variables
    """
    def __init__(self, filepath):
        self.variables = {}
        self.letters = []
        self.query = None

        with open(filepath) as reader:
            self.letters = reader.readline().rstrip().split(' ')
            for letter in self.letters:
                self.variables[letter] = Variable(letter)

            # Read conditional probabilities until we hit an empty line
            for line in iter(reader.readline, '\n'):
                # e.g "+A +B C 0.2" -> ['+A', '+B', 'C', '0.2']
                components = line.rstrip().split(' ')
                # Will assign 
                self.process_components(components)

            # Finally, read the query
            line = reader.readline()
            query_components = line.rstrip().split(' ')
            dep_var = query_components.pop(0)
            self.query = Query(dep_var, query_components)

    def process_components(self, components):
        """
        Updates Bayes Net probabilities and structure. 
        components : list describing a conditional probability from the Bayes Net
                     (ex: ['+A', '-B', 'C', '0.5'] -> P(+C | +A, -B) = 0.5)

        """
        probability = float(components.pop())
        # probability = 0.5, components = ['+A', '-B', 'C']
        dep_var = components.pop()
        # dep_var = 'C', components = ['+A', '-B']
        parents = [s[1] for s in components]
        # parents = ['A', 'B']
        values = tuple((s[0]=="+") for s in components)
        # values = [True, False]
        
        if (len(parents) > 0):
            self.variables[dep_var].parents = parents
            # self.variables['C'].parents = ['A', 'B']
            self.add_children(dep_var, parents)
            # self.add_children('C', ['A', 'B'])
            self.variables[dep_var].distribution[values] = probability
            # self.variables['C'].probability = 0.5
        else:
            self.variables[dep_var].probability = probability
            # self.variables['C'].probability = 0.5
    
    def add_children(self, dep_var, parents):
        """
        Add dep_var to the children list of each parent
        """
        for parent in parents:
            if dep_var not in self.variables[parent].children:
                self.variables[parent].children.append(dep_var)

    def sample(self, probability):
        """
        Use this function when generating random assignments.
        You should not be generating random numbers elsewhere.
        """
        return random.uniform(0, 1) < probability

    def direct_sample(self, trial_count):
        """
        Example of a direct sampling implementation. Ignores evidence variables.
        You do not need to edit this.
        """
        count = 0

        for i in xrange(trial_count):
            values = {}

            for letter in self.letters:
                prob = self.variables[letter].get_prob(values)
                values[letter] = self.sample(prob)

            if values[self.query.variable]:
                count += 1

        return float(count) / trial_count

    def rejection_sample(self, trial_count):
        """
        Returns the estimated probability of the query using rejection method.
        Ignore any samples that result in any invalid evidence variables.
        """
        count = 0
        valid_trial_count = 1

        for i in xrange(trial_count):
            values = {}

            valid_sample = True

            for letter in self.letters:
                prob = self.variables[letter].get_prob(values)
                values[letter] = self.sample(prob)

                if letter in self.query.evidence:
                    if (self.query.evidence[letter] != values[letter]):
                        valid_sample = False
                        break

            if valid_sample:
                valid_trial_count += 1

                if values[self.query.variable]:
                    count += 1

        return float(count) / valid_trial_count

    def likelihood_sample(self, trial_count):
        """
        Returns the estimated probability of the query using likelihood weight.
        Here, we iterate through the variables in topological order.
        If we reach an evidence variable, we fix it to the correct value and
        accumulate the evidence variable's probability to our weight.
        We also keep a running total of all weights.
        At the end, we divide all the weights of the valid queries over the
        total weights.
        """
        count = 0

        sum_query_weights = 0
        sum_total_weights = 0

        for i in xrange(trial_count):
            values = {}

            sample_weight = 1.0

            for letter in self.letters:
                prob = self.variables[letter].get_prob(values)

                # Fix the evidence variables
                if letter in self.query.evidence:
                    values[letter] = self.query.evidence[letter]

                    if (values[letter]):
                        sample_weight *= prob
                    else:
                        sample_weight *= (1 - prob)
                else:
                    values[letter] = self.sample(prob)

            if values[self.query.variable]:
                sum_query_weights += sample_weight

            sum_total_weights += sample_weight

        return float(sum_query_weights) / sum_total_weights

    def gibbs_sample(self, trial_count):
        """
        Implement this!
        Returns the estimated probability of the query, using gibbs method.
        """
        values = {}
        count = total_trials = 0

        # Initialize
        for letter in self.letters:
            if (letter in self.query.evidence):
                # Fix evidence variables
                values[letter] = self.query.evidence[letter]
            else:
                # Initialize non-evidence to True
                values[letter] = True

        # Collect non-evidence variables
        non_evidence_letters = []
        for letter in self.letters:
            if (letter not in self.query.evidence):
                non_evidence_letters.append(letter)

        for i in xrange(trial_count):
            for letter in non_evidence_letters:

                # Probability of x, given its parents
                pos_prob = self.variables[letter].get_prob(values)
                # Probability of x's children, given their parents
                values[letter] = True # FIX TO BE TRUE
                for child in self.variables[letter].children:
                    child_prob = self.variables[child].get_prob(values)

                    if (values[child]):
                        pos_prob *= child_prob
                    else:
                        pos_prob *= (1 - child_prob)

                ### DO SAME THING FOR FALSE PROB

                # Probability of x, given its parents
                neg_prob = 1 - self.variables[letter].get_prob(values)
                # Probability of x's children, given their parents
                values[letter] = False # FIX TO BE FALSE
                for child in self.variables[letter].children:
                    child_prob = self.variables[child].get_prob(values)

                    if (values[child]):
                        neg_prob *= child_prob
                    else:
                        neg_prob *= (1 - child_prob)

                ### NORMALIZE
                prob = pos_prob / (pos_prob + neg_prob)

                ### SAMPLE
                values[letter] = self.sample(prob)

                if values[self.query.variable]:
                    count += 1

                total_trials += 1

        return float(count) / total_trials 

class Variable:
    """
    letter: the letter (ex: 'A')
    distribution: dictionary mapping ordered values of parents to float probabilities,
                  ex: (True, True, False) -> 0.5
    parents: list of parents (ex: ['C', 'D'])
    children: list of children (ex: ['E'])
    probability: probability of node if the node has no parents
    """
    def __init__(self, letter):
        self.letter = letter
        self.distribution = {} # Maps values of parents (ex: True, True, False) to
        self.parents = []
        self.children = []
        self.probability = 0.0 # Only for variables with no parents

    def get_prob(self, values):
        if len(self.parents) == 0:
            return self.probability
        else:
            key = tuple([values[letter] for letter in self.parents])
            return self.distribution[key]

class Query:
    """
    self.variable: the dependent variable associated with the query
    self.evidence: mapping from evidence variables to True or False
    """
    def __init__(self, variable, evidence):

        self.variable = variable
        self.evidence = {}
        for s in evidence: # ex: "+B" or "-C"
            self.evidence[s[1]] = (s[0] == "+")
            # {'B':True, 'C':False}

if __name__ == '__main__':
    # filename = sys.argv[1]
    # bayes_net = BayesNet(filename)

    # print "REJECTION SAMPLING..."
    # for i in xrange(1, 50):
    #     print bayes_net.rejection_sample(i)

    # print "\nLIKELIHOOD SAMPLING..."
    # for i in xrange(1, 50):
    #     print bayes_net.likelihood_sample(i)

    # print "\nBAYTES SAMPLING..."
    # for i in xrange(1, 50):
    #     print bayes_net.gibbs_sample(i)

    filename = sys.argv[1]
    trial_count = int(sys.argv[2])
    sampling_type = int(sys.argv[3])
    bayes_net = BayesNet(filename)

    if sampling_type == 0:
        print bayes_net.direct_sample(trial_count)
    elif sampling_type == 1:
        print bayes_net.rejection_sample(trial_count)
    elif sampling_type == 2:
        print bayes_net.likelihood_sample(trial_count)
    elif sampling_type == 3:
        print bayes_net.gibbs_sample(trial_count)