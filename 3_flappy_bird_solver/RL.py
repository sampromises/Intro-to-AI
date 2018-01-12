'''
Author: Sam Kim

Using TensorFlow and Keras APIs to implement a Flappy Bird solver, achieving a
high score of 300+.

'''

RANDOM_SEED = 715

import numpy as np
import random
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

from tensorflow import set_random_seed, Session, ConfigProto
set_random_seed(RANDOM_SEED)

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop
from keras import backend
from keras.initializers import lecun_uniform

sess = Session(config=ConfigProto(inter_op_parallelism_threads=1))
backend.set_session(sess)


"""
Here are two values you can use to tune your Qnet
You may choose not to use them, but the training time
would be significantly longer.
Other than the inputs of each function, this is the only information
about the nature of the game itself that you can use.
"""
PIPEGAPSIZE  = 100
BIRDHEIGHT = 24

class QNet(object):

    def __init__(self):
        """
        Initialize neural net here.
        You may change the values.

        Args:
            num_inputs: Number of nodes in input layer
            num_hidden1: Number of nodes in the first hidden layer
            num_hidden2: Number of nodes in the second hidden layer
            num_output: Number of nodes in the output layer
            lr: learning rate
        """
        self.num_inputs = 2
        self.num_hidden1 = 10
        self.num_hidden2 = 10
        self.num_output = 2
        # self.lr = 0.001
        # self.lr = 0.0055
        # self.lr = 0.01
        self.lr = 0.05
        # self.lr = 0.075
        self.build()

        self.states = []
        self.updates = []
        self.minibatch_size = 1 #50
        self.maxbatch_size = 1 #400
        self.count = 0
        self.my_score = 0
        self.high_score = -1

        ### FOR REPORT 4 ###
        self.flap_count = 0
        self.scores_data = []
        self.counts_data = []
        self.flaps_data = []

    def build(self):
        """
        Builds the neural network using keras, and stores the model in self.model.
        Uses shape parameters from init and the learning rate self.lr.
        You may change this, though what is given should be a good start.
        """
        model = Sequential()
        # model.add(Dense(self.num_hidden1, init='lecun_uniform', input_shape=(self.num_inputs,)))
        model.add(Dense(self.num_hidden1, init=lecun_uniform(seed=RANDOM_SEED), input_shape=(self.num_inputs,)))
        model.add(Activation('relu'))

        # model.add(Dense(self.num_hidden2, init='lecun_uniform'))
        model.add(Dense(self.num_hidden2, init=lecun_uniform(seed=RANDOM_SEED)))
        model.add(Activation('relu'))

        # model.add(Dense(self.num_output, init='lecun_uniform'))
        model.add(Dense(self.num_output, init=lecun_uniform(seed=RANDOM_SEED)))
        model.add(Activation('linear'))

        rms = RMSprop(lr=self.lr)
        model.compile(loss='mse', optimizer=rms)
        self.model = model

    def flap(self, input_data):
        """
        Use the neural net as a Q function to act.
        Use self.model.predict to do the prediction.

        Args:
            input_data (Input object): contains information you may use about the 
            current state.

        Returns:
            (choice, prediction, debug_str): 
                choice (int) is 1 if bird flaps, 0 otherwise. Will be passed
                    into the update function below.
                prediction (array-like) is the raw output of your neural network,
                    returned by self.model.predict. Will be passed into the update function below.
                debug_str (str) will be printed on the bottom of the game
        """

        # state = your state in numpy array
        # prediction = self.model.predict(state.reshape(1, self.num_inputs), batch_size=1)[0]
        # choice = make choice based on prediction
        # debug_str = ""
        # return (choice, prediction, debug_str)
        
        state = np.array([input_data.distX, input_data.distY])
        prediction = self.model.predict(state.reshape(1, self.num_inputs), batch_size=1)[0]
        choice = (prediction[0] > prediction[1])
        debug_str = "HI-SCORE: %d | FLAPS: %d" % (self.high_score, self.flap_count)

        return (choice, prediction, debug_str)

    def update(self, last_input, last_choice, last_prediction, crash, scored, playerY, pipVelX):
        """
        Use Q-learning to update the neural net here
        Use self.model.fit to back propagate

        Args:
            last_input (Input object): contains information you may use about the
                input used by the most recent flap() 
            last_choice: the choice made by the most recent flap()
            last_prediction: the prediction made by the most recent flap()
            crash: boolean value whether the bird crashed
            scored: boolean value whether the bird scored
            playerY: y position of the bird, used for calculating new state
            pipVelX: velocity of pipe, used for calculating new state

        Returns:
            None
        """
        # This is how you calculate the new (x,y) distances
        # new_distX = last_input.distX + pipVelX
        # new_distY = last_input.pipeY - playerY

        # state = compute new state in numpy array
        # reward = compute your reward
        # prediction = self.model.predict(state.reshape(1, self.num_inputs), batch_size = 1)

        new_distX = last_input.distX + pipVelX
        new_distY = last_input.pipeY - playerY

        state = np.array([new_distX, new_distY])

        # CALCULATING OLD STATE
        old_state = np.asarray([last_input.distX, last_input.distY])

        ######################### SCORE COUNTER #########################
        ## FOR REPORT 4 ##
        if (last_choice):
            self.flap_count += 1

        if (scored):
            self.my_score += 1

            ## FOR REPORT 4 ##
            # if (self.my_score == 50):
            #     self.high_score = self.my_score
                ## FOR REPORT 4 ##
                # self.scores_data.append(self.high_score)
                # self.counts_data.append(self.count)
                # self.flaps_data.append(self.flap_count)
                # print "LR: ", self.lr
                # print "SCORES: ", self.scores_data
                # print "COUNTS: ", self.counts_data
                # print "FLAPS: ", self.flaps_data
                # raise Exception, "REACHED SCORE OF 50!!!"

        if (crash):
            ## FOR REPORT 4 ##
            if (self.my_score > self.high_score):
                self.high_score = self.my_score
                ## FOR REPORT 4 ##
                # self.scores_data.append(self.high_score)
                # self.counts_data.append(self.count)
                # self.flaps_data.append(self.flap_count)

            self.my_score = 0


        ######################### REWARD #########################


        (distX, distY) = (last_input.distX, last_input.distY)
        (playerX, playerY) = (last_input.playerX, last_input.playerY)
        (pipeX, pipeY) = (last_input.pipeX, last_input.pipeY)

        underGap = (distY <= BIRDHEIGHT)
        comfyUnderGap = (distY <= 2*BIRDHEIGHT)
        overGap = (distY >= PIPEGAPSIZE - BIRDHEIGHT)

        center = pipeY + PIPEGAPSIZE / 2
        distFromCenter = np.abs(playerY - center)

        reward = 0

        # BETTER reward for being closer to center of pipes
        if (not comfyUnderGap and not overGap):
            reward += 20

        # Reward for being under pipe and flapping
        if (last_choice and underGap):
            reward += 10
        else:
            reward -= 10

        # Reward for being over and not flapping
        if (not last_choice and overGap):
            reward += 10
        else:
            reward -= 10

        # Penalize for dying
        if (crash):
            reward -= 20

        # Reward for scoring
        if (scored):
            reward += 20


        ######################### PREDICTION W/ BATCHES #########################
        discount_factor = 0.4

        prediction = self.model.predict(state.reshape(1, self.num_inputs), batch_size=1)

        y = float(reward) + discount_factor * np.max(prediction)

        updated_prediction = last_prediction
        if (last_choice):
            updated_prediction[0] = y
        else:
            updated_prediction[1] = y

        # Build up the mini-batch
        if (len(self.states) < self.maxbatch_size):
            self.states.append(old_state)
            self.updates.append(updated_prediction)

            self.count += 1
        # Filling up the max-batch
        else:

            self.states.pop(0)
            self.updates.pop(0)
            self.states.append(old_state)
            self.updates.append(updated_prediction)

            if (self.my_score < 3): # RANDOMLY SAMPLE, EVERY ITERATION

                random_states = []
                random_updates = []
                sample_indices = random.sample(range(0,len(self.states)), self.minibatch_size)
                for i in sample_indices:
                    random_states.append(self.states[i])
                    random_updates.append(self.updates[i])

                assert (len(random_states) == self.minibatch_size)

                self.model.fit (np.asarray(random_states), np.asarray(random_updates),
                    batch_size=self.minibatch_size, epochs=1,
                    verbose=0)

            assert (len(self.states) == len(self.updates))

            self.count += 1

        
class Input:
    def __init__(self, playerX, playerY, pipeX, pipeY, distX, distY):
        """
        playerX: x position of the bird
        playerY: y position of the bird
        pipeX: x position of the next pipe
        pipeY: y position of the next pipe
        distX: x distance between the bird and the next pipe
        distY: y distance between the bird and the next pipe
        """
        self.playerX = playerX
        self.playerY = playerY
        self.pipeX = pipeX
        self.pipeY = pipeY
        self.distX = distX
        self.distY = distY