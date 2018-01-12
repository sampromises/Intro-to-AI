'''
Author: Sam Kim

An implementation of the CFR+ algorithm to choose the best strategy in
non-perfect imperfect games.

'''

#####################################################################
# Before implementing CFR, it will be helpful to take a look
# at the helper methods in game.py. These are the methods you
# need to interact with when you traverse the game tree in
# CFR.
#####################################################################
import sys
from game import Game
import random

DEBUG = 1

######################################################
# Add any classes or helper functions you want here
######################################################

# Helper debug function to print current strategy
def print_strategy_profile(strategy_profile):
    print "STRATEGY_PROFILE:"
    for p in xrange(len(strategy_profile)):
        print "\tplayer:", p
        for i in xrange(len(strategy_profile[p])):
            print "\t\tinfoset:", i
            print "\t\t\taction probabilities:", strategy_profile[p][i]

# Helper debug function to print current regrets
def print_regrets(regrets):
    print "REGRETS:"
    for p in xrange(len(regrets)):
        print "\tplayer:", p
        for i in xrange(len(regrets[p])):
            print "\t\tinfoset:", i
            print "\t\t\taction regrets:", regrets[p][i]

# Helper debug function to print current strategy_sums
def print_strategy_sums(strategy_sums):
    print "STRATEGY_SUMS:"
    for p in xrange(len(strategy_sums)):
        print "\tplayer:", p
        for i in xrange(len(strategy_sums[p])):
            print "\t\tinfoset:", i
            print "\t\t\taction strategy sums:", strategy_sums[p][i]

# Initialize strategy_profile, regret totals, and strategy sums
#   Initialize strategy to be uniform distribution,
#   initialize regrets and strategy sums to be 0
def initialize_data(g, strategy_profile, regrets, strategy_sums):
    n = g.get_num_nodes()

    # Initialize strategy_profile dicts
    for node_id in xrange(n):
        if (node_id not in g.node_nature_probabilities and not g.is_leaf(node_id)):

            p = g.get_current_player(node_id)
            i = g.node_infoset[node_id]
            actions = g.get_num_actions_node(node_id)

            uni_prob = float(1) / g.get_num_actions_infoset(p, i)

            # Add player key
            if p not in regrets:
                strategy_profile[p] = {}
                regrets[p] = {}
                strategy_sums[p] = {}

            # Add infoset key
            if i not in strategy_profile[p]:
                strategy_profile[p][i] = {}
                regrets[p][i] = {}
                strategy_sums[p][i] = {}

            # Add action keys
            for a in xrange(actions):
                # Uniform probability values
                strategy_profile[p][i][a] = uni_prob

                # Initialize regrets
                regrets[p][i][a] = 0

                # Initialize strategy_sums
                strategy_sums[p][i][a] = 0

# Set all negative regrets to 0
def make_regrets_nonzero(regrets):
    for p in xrange(len(regrets)):
        for i in xrange(len(regrets[p])):
            for a in xrange(len(regrets[p][i])):
                if (regrets[p][i][a] < 0):
                    regrets[p][i][a] = 0

# Normalize the strategy sums obtained and apply them as the new probabilities
def normalize_strategy_sums(strategy_profile, strategy_sums):
    for p in xrange(len(strategy_sums)):
        for i in xrange(len(strategy_sums[p])):
            sums = []
            for a in xrange(len(strategy_sums[p][i])):
                sums.append(strategy_sums[p][i][a])

            try:
                norm_sums = [float(j)/sum(sums) for j in sums]

                for a2 in xrange(len(norm_sums)):
                    strategy_profile[p][i][a2] = norm_sums[a2]
            except:
                pass

# Reset the probabilities, used after each iteration
def reset_strategy_profile(strategy_profile):
    for p in strategy_profile:
        for i in strategy_profile[p]:
            uni_prob = float(1) / len(strategy_profile[p][i])
            for a in strategy_profile[p][i]:
                strategy_profile[p][i][a] = uni_prob

# Updates all probabilities, proportional to positive regrets
def update_probabilities(strategy_profile, regrets, p, i, actions, iter_num):
    # Sum all positive regrets
    total_regret = 0.0
    for a in xrange(actions):
        total_regret += max(regrets[p][i][a], 0)

    if (total_regret <= 0):
        uni_prob = 1 / float(actions)
        for a in xrange(actions):
            strategy_profile[p][i][a] = uni_prob
    else:
        # Regret of current action
        for a in xrange(actions):
            curr_action_regret = max(regrets[p][i][a], 0)
            new_prob = (curr_action_regret / float(total_regret))
            strategy_profile[p][i][a] = new_prob

# function CFR(node, reach, p)  //Call CFR(Initial, 1, p) at the start of each traversal, where p alternates between P1 and P2.
def cfr_plus(g, strategy_profile, regrets, strategy_sums, visited, node_id, reach, p, iter_num):

    # if (node is terminal) then
    if g.is_leaf(node_id):
        # return node.value[p] * reach
        utility = g.get_leaf_utility(node_id)
        if (p == 0):
            # Util is for first player
            return utility * reach
        else:
            # Negative util for second player
            return (-utility) * reach
    # else
    else:
        # ev = 0
        ev = 0.0
        # if (node is chance) then
        if node_id in g.node_nature_probabilities:
            # for each action in node:
            actions = g.get_num_actions_node(node_id)
            for a in xrange(actions):
                # ev += CFR(node.do_action(action), reach * prob[action], p)
                next_node_id = g.get_child_id(node_id, a)
                next_reach = reach * (g.node_nature_probabilities[node_id][a])
                ev += cfr_plus(g, strategy_profile, regrets, strategy_sums, visited, next_node_id, next_reach, p, iter_num)
        # else
        else:
            # set probabilities for actions in proportion to positive regret
            # (if it is the first time this information set is encountered this traversal)
            i = g.get_node_infoset(node_id)

            if g.get_current_player(node_id) is not p:
                p_traversal = g.get_current_player(node_id)
            else:
                p_traversal = p

            curr_infoset = (p_traversal, i)

            if (curr_infoset not in visited):
                actions = g.get_num_actions_node(node_id)
                update_probabilities(strategy_profile, regrets, p_traversal, i, actions, iter_num)
                visited.add(curr_infoset)


            # if (node.whose_turn == p):
            if (g.get_current_player(node_id) == p):
                # for each action in node:
                    # action_ev[action] = CFR(node.do_action(action), reach, p)  //get the value for taking this action
                    # ev += prob[action] * action_ev[action]
                # for each action in node:
                    # node.regret[action] += (action_ev[action] - ev) //update the regret for each action
                actions = g.get_num_actions_node(node_id)
                action_ev_l = []
                for a in xrange(actions):
                    next_node_id = g.get_child_id(node_id, a)
                    action_ev = cfr_plus(g, strategy_profile, regrets, strategy_sums, visited, next_node_id, reach, p, iter_num)
                    action_ev_l.append(action_ev)
                    ev += (strategy_profile[p][i][a]) * action_ev

                for a in xrange(actions):
                    regrets[p][i][a] += (action_ev_l[a] - ev)
            # else
            else:
                p_to_update = g.get_current_player(node_id) # NEED BECAUSE WE'RE IN THE OTHER PLAYER'S NODE

                # for each action in node:
                    # node.stored_strategy[action] += reach * prob[action]  //update the average strat (normalize at the end)
                    # ev += CFR(node.do_action(action), reach * prob[action], p)
                actions = g.get_num_actions_node(node_id)
                for a in xrange(actions):
                    strategy_sums[p_to_update][i][a] += reach * (strategy_profile[p_to_update][i][a]) * iter_num

                    next_node_id = g.get_child_id(node_id, a)
                    next_reach = reach * (strategy_profile[p_to_update][i][a])
                    ev += cfr_plus(g, strategy_profile, regrets, strategy_sums, visited, next_node_id, next_reach, p, iter_num)
        # return ev
        return ev

# game will be an instance of Game, which is defined in game.py
# num_iterations is the number of CFR+ iterations you should perform.
# An iteration of CFR+ is one traversal of the entire game tree for each player.
def solve_game(game, num_iterations):
#############################
    # The goal of your algorithm is to fill
    # strategy_profile with equilibrium strategies.
    # strategy_profile[p][i][a] should return
    # the probability of player p choosing the particular
    # action a at information set i in the equilibrium
    # you compute.
    #
    # An example set of values for a small game with 2
    # information sets for each player would be:
    #    strategy_profile[0][0] = [0.375, 0.625]
    #    strategy_profile[0][1] = [1,0]
    #
    #    strategy_profile[1][0] = [0.508929, 0.491071]
    #    strategy_profile[1][1] = [0.666667, 0.333333]
    strategy_profile = {}

    # Data structures to hold regrets and strategy sums
    regrets = {}
    strategy_sums = {}

    # Initialize everything
    initialize_data(game, strategy_profile, regrets, strategy_sums)

    #######################
    # Implement CFR+ in here
    #######################
    visited = set()
    for i in xrange(1, (4*num_iterations)+1):
        reach = 1.0
        # Reinitialize visited after each 'iteration' (2 traversals, 1 by each player)
        if (i % 2 == 0):
            visited = set()

        cfr_plus(game, strategy_profile, regrets, strategy_sums, visited, game.get_root(), reach, (i%2), i)

        make_regrets_nonzero(regrets)

    normalize_strategy_sums(strategy_profile, strategy_sums)

    return strategy_profile


if __name__ == "__main__":
    # feel free to add any test code you want in here. It will not interfere with our testing of your code.
    # currently, this file can be invoked with:
    # python cfr.py <path/to/gamefile> <num CFR+ iterations>

    filename = sys.argv[1]
    iterations = int(sys.argv[2])

    game = Game()
    game.read_game_file(filename)

    strategy_profile = solve_game(game, iterations)
    #print "Expected Value: " + str(game.compute_strategy_profile_ev(strategy_profile))
    print "Exploitability: " + str(game.compute_strategy_profile_exp(strategy_profile))
