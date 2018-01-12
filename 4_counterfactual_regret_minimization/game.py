import sys
import shlex

class Game:
    def __init__(self):
        self.root = 0
        self.num_nodes = 0
        self.total_num_actions = 0
        self.num_chance_histories = 0
        self.num_combined_player_histories = 0
        self.num_terminal_histories = 0
        self.infoset_num_actions = {0:{}, 1:{}}
        self.infoset_nodes = {0:{}, 1:{}}
        self.node_children = {}
        self.node_player = {}
        self.node_infoset = {}
        self.node_names = {}
        self.node_utility = {}
        self.node_num_actions = {}
        self.node_action_names = {}
        self.node_nature_probabilities = {}
        self.num_infosets = {}

        self.node_height = {}
        self.height = {0:{}, 1:{}}
        self.action_value = {0:{}, 1:{}}
        self.last_touched = {0:{}, 1:{}}



    ###############################################
    # Helper methods for accessing game information
    ###############################################
    def get_root(self):
        return self.root

    # Returns the number of actions in a non-terminal node
    def get_num_actions_node(self,node_id):
        if not node_id in self.node_num_actions:
            print "Error: Attempted to get number of actions for a leaf node"
        return self.node_num_actions[node_id]

    # Returns the number of actions in a player's information set
    def get_num_actions_infoset(self,player,infoset):
        if not player in [0,1] or not infoset in self.infoset_num_actions[player]:
            print "Error: Attempted to get number of actions for a leaf node"
        return self.infoset_num_actions[player][infoset]

    # Returns the node following this node/action pair
    def get_child_id(self, node_id, action):
        return self.node_children[node_id][action]

    # Returns the player who acts at this node, or -1 for chance/nature
    def get_current_player(self, node_id):
        return self.node_player[node_id]

    # Returns this node's information set
    def get_node_infoset(self, node_id):
        return self.node_infoset[node_id]

    # Returns true if this is a terminal node
    def is_leaf(self, node_id):
        return node_id in self.node_utility

    # Returns the utility of a terminal node (for the first player!)
    def get_leaf_utility(self, node_id):
        if not self.is_leaf(node_id):
            print "Error: Attempted to get utility of a non-leaf node"
        return self.node_utility[node_id]

    # Returns the probability of a chance node's action
    def get_nature_probability(self, node_id, action):
        if not node_id in self.node_nature_probabilities:
            print "Error: Attempted to get nature probability for a non-nature node"
        return self.node_nature_probabilities[node_id][action]

    def get_num_infosets(self, player):
        return self.num_infosets[player]

    def get_num_nodes(self):
        return self.num_nodes

    def print_game_info(self):
        print "Num nodes: " + str(self.num_nodes)
        print "Num infosets: " + str(self.num_infosets)
        print "Num chance histories: " + str(self.num_chance_histories)
        print "Num terminal histories: " + str(self.num_terminal_histories)

    def print_game_tree(self):
        print "Root: " + str(self.root)
        for i in range(0, self.num_nodes):
            self.print_node_info(i)

    def print_node_info(self, node_id):
        print str(node_id),
        print " "+ str(self.node_names[node_id]),
        if self.is_leaf(node_id):
            print "leaf, utility: " + str(self.node_utility[node_id])
        elif node_id in self.node_nature_probabilities:
            print ", nature",
            print ", actions: " + str(self.node_action_names[node_id]), 
            print ", children: " + str(self.node_children[node_id]),
            print ", probabilities : " + str(self.node_nature_probabilities[node_id])
        else:
            infoset = self.node_infoset[node_id]
            print ", player " + str(self.get_current_player(node_id)),
            print ", infoset: " + str(infoset), 
            print ", actions: " + str(self.node_action_names[node_id]),
            print ", children: " + str(self.node_children[node_id])

    ##############################################################
    # End of helper methods, you can ignore everything below here.
    ##############################################################

    def compute_strategy_profile_ev(self, strategy_profile):
        return self.compute_strategy_profile_ev_rec(strategy_profile, self.get_root())

    def compute_strategy_profile_ev_rec(self, strategy_profile, current):
        if self.is_leaf(current):
            return self.get_leaf_utility(current)

        val = 0
        player = self.get_current_player(current)

        for i in range(0, self.get_num_actions_node(current)):
            child_id = self.get_child_id(current, i)
            if player == -1:
                prob = self.get_nature_probability(current, i)
            else:
                infoset = self.get_node_infoset(current)
                prob = strategy_profile[player][infoset][i]
            val += prob * self.compute_strategy_profile_ev_rec(strategy_profile, child_id)

        return val


    def compute_strategy_profile_exp(self, strategy_profile):
        exp0 = 0
        exp1 = 0
        self.exploitability_initialize()
        self.compute_height(self.get_root())
        for p in range(2):
            #self.exploitability_initialize()
            for t in range(self.node_height[self.get_root()] + 2):
                if (p == 0):
                    exp0 = self.compute_strategy_profile_exp_rec(p, self.get_root(), 1.0, t, strategy_profile)
                else:
                    exp1 = self.compute_strategy_profile_exp_rec(p, self.get_root(), 1.0, t, strategy_profile)
        return exp1 + exp0

    def exploitability_initialize(self):
        for p in range(2):
            infosets = self.get_num_infosets(p)
            for infoset in range(infosets):
                self.action_value[p][infoset] = [0] * self.get_num_actions_infoset(p, infoset)
                self.height[p][infoset] = -1
                self.last_touched[p][infoset] = -1
        nodes = self.get_num_nodes()
        for node in range(nodes):
            self.node_height[node] = -1

    def compute_height(self, nid):
        if (self.is_leaf(nid)):
            return -1
        else:
            num_actions = self.get_num_actions_node(nid)
            max_height = -1
            for action in range(num_actions):
                action_height = self.compute_height(self.get_child_id(nid, action))
                if (max_height == -1 or action_height > max_height):
                    max_height = action_height
            self.node_height[nid] = max_height + 1
            if (self.get_current_player(nid) != -1):
                infoset = self.get_node_infoset(nid)
                player = self.get_current_player(nid)
                if (self.height[player][infoset] == -1 or self.height[player][infoset] > self.node_height[nid]):
                    self.height[player][infoset] = self.node_height[nid]
            return self.node_height[nid]

    def compute_strategy_profile_exp_rec(self, p, nid, reach, t, strategy_profile):
        if (self.is_leaf(nid)):
            if (p == 0):
                val = reach * float(self.get_leaf_utility(nid))
                return val
            else:
                val = -reach * float(self.get_leaf_utility(nid))
                return val
        elif (self.get_current_player(nid) == -1):
            num_actions = self.get_num_actions_node(nid)
            ev = 0.0
            for action in range(num_actions):
                prob = self.get_nature_probability(nid, action)
                ev += self.compute_strategy_profile_exp_rec(p, self.get_child_id(nid, action), reach * prob, t, strategy_profile)
            return ev
        else:
            infoset = self.get_node_infoset(nid)
            player = self.get_current_player(nid)
            num_actions = self.get_num_actions_infoset(player, infoset)

            if (player == p):
                if (t > self.height[player][infoset]):
                    max_action = -1
                    max_value = 0
                    for action in range(num_actions):
                        if (max_action == -1 or max_value < self.action_value[player][infoset][action]):
                            max_action = action
                            max_value = self.action_value[player][infoset][action]
                    return self.compute_strategy_profile_exp_rec(p, self.get_child_id(nid, max_action), reach, t, strategy_profile)
                else:
                    if (self.last_touched[player][infoset] < t):
                        self.last_touched[player][infoset] = t
                        for action in range(num_actions):
                            self.action_value[player][infoset][action] = 0
                    for action in range(num_actions):
                        self.action_value[player][infoset][action] += self.compute_strategy_profile_exp_rec(p, self.get_child_id(nid, action), reach, t, strategy_profile)
                    return 0
            else:
                ev = 0.0

                prob_sum = 0.0
                for action in range(num_actions):
                    prob_sum += strategy_profile[player][infoset][action]

                prob = 1.0 / float(num_actions)
                for action in range(num_actions):
                    if (prob_sum > 0.0):
                        prob = strategy_profile[player][infoset][action] / prob_sum
                    ev += self.compute_strategy_profile_exp_rec(p, self.get_child_id(nid, action), reach * prob, t, strategy_profile)
                return ev

    def read_game_file(self, filename):
        for line in open(filename):
            line = line.strip('\t \n')
            split_line = shlex.split(line)
            if line[0] == '#':
                continue
            elif split_line[0].isdigit():
                node_id = int(split_line[0])
                self.node_set_general_information(split_line, node_id)
                if len(split_line) == 3 or len(split_line) == 5:
                    self.create_leaf_node(split_line)
                elif node_id < self.num_chance_histories: # nature node
                    self.create_nature_node(split_line)
                else: # player node
                    self.create_player_node(split_line)
            else:
                self.read_game_info(line)


    def read_game_info(self, line):
        split_line = line.split(' ')
        self.num_chance_histories = int(split_line[1]);
        self.num_combined_player_histories = int(split_line[2]);
        self.num_terminal_histories = int(split_line[3]);
        self.num_nodes =  int(split_line[5]) + 1;
        self.num_infosets[0] = int(split_line[7]);
        self.num_infosets[1] = int(split_line[8]);

    def node_set_general_information(self, line, node_id):
        name = line[1]
        if name == '/':
            self.root = node_id

    def create_player_node(self, line):
        node_id = int(line[0])
        self.node_names[node_id] = line[1]
        player = int(line[2])
        infoset = int(line[3])
        num_actions = int(line[4])
        self.infoset_num_actions[player][infoset] = num_actions
        self.node_num_actions[node_id] = num_actions
        self.node_infoset[node_id] = infoset
        self.node_player[node_id] = player
        self.node_action_names[node_id] = []
        if infoset in self.infoset_nodes[player]:
            self.infoset_nodes[player][infoset].append(node_id)
        else:
            self.infoset_nodes[player][infoset] = [node_id]

        self.node_children[node_id] = []
        for action in range(0, num_actions):
            child_id = int(line[6+2*action])
            action_name = line[5+2*action]
            self.node_action_names[node_id].append(action_name)
            self.node_children[node_id].append(child_id);


    def create_nature_node(self, line):
        node_id = int(line[0])
        self.node_names[node_id] = line[1]
        self.node_player[node_id] = -1
        num_actions = int(line[2])
        self.node_num_actions[node_id] = num_actions
        sum = 0
        self.node_action_names[node_id] = []
        self.node_children[node_id] = []
        for i in range(0, num_actions):
            child_id = int(line[4+3*i])
            self.node_children[node_id].append(child_id);
            action_name = line[3+3*i]
            self.node_action_names[node_id].append(action_name)
            sum += int(line[5+3*i])

        self.node_nature_probabilities[node_id] = []
        for i in range(0, num_actions):
            prob = float(line[5+3*i]) / sum
            self.node_nature_probabilities[node_id].append(prob)


    def create_leaf_node(self, line):
        node_id = int(line[0])
        self.node_names[node_id] = line[1]
        utility = int(line[2])
        self.node_utility[node_id] = utility



if __name__ == "__main__":
    filename = sys.argv[1]
    game = Game()
    game.read_game_file(filename)

    if len(sys.argv) > 2 and sys.argv[2] == 'game_info':
        game.print_game_info()
    elif len(sys.argv) > 2 and sys.argv[2] == 'game_tree':
        game.print_game_tree()
    elif 'coin' in filename:
        equilibrium_profile = {}
        equilibrium_profile[0] = {}
        equilibrium_profile[0][0] = [0.375, 0.625]
        equilibrium_profile[0][1] = [1,0]
        equilibrium_profile[0][2] = [0.333333, 0.666667]
        equilibrium_profile[0][3] = [0.2, 0.8]
        equilibrium_profile[0][4] = [1,0]

        equilibrium_profile[1] = {}
        equilibrium_profile[1][0] = [0.508929, 0.491071]
        equilibrium_profile[1][1] = [0.666667, 0.333333]
        equilibrium_profile[1][2] = [0.8, 0.2]

        print game.compute_strategy_profile_ev(equilibrium_profile)

    elif 'kuhn' in filename:
        equilibrium_profile = {}
        equilibrium_profile[0] = {}
        equilibrium_profile[0][0] = [0.666667, 0.333333]
        equilibrium_profile[0][1] = [1,0]
        equilibrium_profile[0][2] = [0,1]
        equilibrium_profile[0][3] = [0,1]
        equilibrium_profile[0][4] = [1,0]
        equilibrium_profile[0][0] = [0.666667, 0.333333]
        equilibrium_profile[0][5] = [1,0]

        equilibrium_profile[1] = {}
        equilibrium_profile[1][0] = [0.666667, 0.333333]
        equilibrium_profile[1][1] = [1,0]
        equilibrium_profile[1][2] = [0,1]
        equilibrium_profile[1][3] = [0,1]
        equilibrium_profile[1][4] = [0.333333, 0.666667]
        equilibrium_profile[1][5] = [1,0]

        print game.compute_strategy_profile_ev(equilibrium_profile)
