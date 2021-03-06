"""
  AO PREENCHER ESSE CABECALHO COM O MEU NOME E O MEU NUMERO USP,
  DECLARO QUE SOU A UNICA PESSOA AUTORA E RESPONSAVEL POR ESSE PROGRAMA.
  TODAS AS PARTES ORIGINAIS DESSE EXERCICIO PROGRAMA (EP) FORAM
  DESENVOLVIDAS E IMPLEMENTADAS POR MIM SEGUINDO AS INSTRUCOES
  DESSE EP E, PORTANTO, NAO CONSTITUEM ATO DE DESONESTIDADE ACADEMICA,
  FALTA DE ETICA OU PLAGIO.
  DECLARO TAMBEM QUE SOU A PESSOA RESPONSAVEL POR TODAS AS COPIAS
  DESSE PROGRAMA E QUE NAO DISTRIBUI OU FACILITEI A
  SUA DISTRIBUICAO. ESTOU CIENTE QUE OS CASOS DE PLAGIO E
  DESONESTIDADE ACADEMICA SERAO TRATADOS SEGUNDO OS CRITERIOS
  DIVULGADOS NA PAGINA DA DISCIPLINA.
  ENTENDO QUE EPS SEM ASSINATURA NAO SERAO CORRIGIDOS E,
  AINDA ASSIM, PODERAO SER PUNIDOS POR DESONESTIDADE ACADEMICA.

  Nome : Henrique Cerquinho
  NUSP : 9793700

  Referencias: Com excecao das rotinas fornecidas no enunciado
  e em sala de aula, caso voce tenha utilizado alguma referencia,
  liste-as abaixo para que o seu programa nao seja considerado
  plagio ou irregular.

  Exemplo:
  - O algoritmo Quicksort foi baseado em:
  https://pt.wikipedia.org/wiki/Quicksort
  http://www.ime.usp.br/~pf/algoritmos/aulas/quick.html
"""

import math
import random
from collections import defaultdict
import util

# **********************************************************
# **            PART 01 Modeling BlackJack                **
# **********************************************************


class BlackjackMDP(util.MDP):
    """
    The BlackjackMDP class is a subclass of MDP that models the BlackJack game as a MDP
    """
    def __init__(self, cardValues, multiplicity, threshold, peekCost):
        """
        cardValues: list of integers (face values for each card included in the deck)
        multiplicity: single integer representing the number of cards with each face value
        threshold: maximum number of points (i.e. sum of card values in hand) before going bust
        peekCost: how much it costs to peek at the next card
        """
        self.cardValues = cardValues
        self.multiplicity = multiplicity
        self.threshold = threshold
        self.peekCost = peekCost

    def startState(self):
        """
         Return the start state.
         Each state is a tuple with 3 elements:
           -- The first element of the tuple is the sum of the cards in the player's hand.
           -- If the player's last action was to peek, the second element is the index
              (not the face value) of the next card that will be drawn; otherwise, the
              second element is None.
           -- The third element is a tuple giving counts for each of the cards remaining
              in the deck, or None if the deck is empty or the game is over (e.g. when
              the user quits or goes bust).
        """
        return (0, None, (self.multiplicity,) * len(self.cardValues))

    def actions(self, state):
        """
        Return set of actions possible from |state|.
        You do not must to modify this function.
        """
        return ['Take', 'Peek', 'Quit']

    def succAndProbReward(self, state, action):
        """
        Given a |state| and |action|, return a list of (newState, prob, reward) tuples
        corresponding to the states reachable from |state| when taking |action|.
        A few reminders:
         * Indicate a terminal state (after quitting, busting, or running out of cards)
           by setting the deck to None.
         * If |state| is an end state, you should return an empty list [].
         * When the probability is 0 for a transition to a particular new state,
           don't include that state in the list returned by succAndProbReward.
        """
        # BEGIN_YOUR_CODE
        """state = (points, peeked card, deck)"""
        """a = (newstate, prob, reward)"""

        newstate = [state[0], state[1], state[2]]
        list = []

        if state[2] == None: # terminal state
            return list

        if action == 'Quit':
            newstate[1] = None
            newstate[2] = None
            a = (tuple(newstate), 1, state[0]) # reward is cur_points
            list.append(a)

        elif action == 'Peek':
            # cannot peek twice in a row
            if state[1] != None:
                return list

            # remaining cards in deck
            rem_cards = sum(state[2])
            for i in range(len(state[2])):
                if state[2][i] != 0:
                    prob = state[2][i] / rem_cards
                    newstate = (state[0], i, state[2])
                    a = (newstate, prob, -self.peekCost)
                    list.append(a)

        elif action == 'Take':
            rem_cards = sum(state[2])

            possible_cards = len(state[2])
            peek = False
            peeked_card = None

            if state[1] != None: # peeked before
                possible_cards = 1
                peek = True

            for i in range(possible_cards):
                # print(possible_cards, state)
                if state[2][i] != 0 or peek:
                    if peek:
                        prob = 1
                        card_value = self.cardValues[state[1]]
                    else:
                        prob = state[2][i] / rem_cards
                        card_value = self.cardValues[i]
                    cur_points = state[0]


                    # didnt bust the score
                    if cur_points + card_value <= self.threshold:
                        cur_points += card_value

                        # update the deck
                        newdeck = []
                        for j in range(len(state[2])):
                            newdeck.append(state[2][j])
                        if peek:
                            newdeck[state[1]] -= 1
                        else:
                            newdeck[i] -= 1
                        if (sum(newdeck) == 0): # deck is empty
                            newdeck = None
                        else:
                            newdeck = tuple(newdeck)

                    # oh boy, busted
                    else:
                        cur_points = 0
                        newdeck = None

                    newstate = (cur_points, None, newdeck)
                    if (newdeck == None): # return points if terminal state
                        a = (newstate, prob, cur_points)
                    else:
                        a = (newstate, prob, 0)
                    list.append(a)

        return list
        # END_YOUR_CODE

    def discount(self):
        """
        Return the descount  that is 1
        """
        return 1

# **********************************************************
# **                    PART 02 Value Iteration           **
# **********************************************************

class ValueIteration(util.MDPAlgorithm):
    """ Asynchronous Value iteration algorithm """
    def __init__(self):
        self.pi = {}
        self.V = {}

    def solve(self, mdp, epsilon=0.001):
        """
        Solve the MDP using value iteration.  Your solve() method must set
        - self.V to the dictionary mapping states to optimal values
        - self.pi to the dictionary mapping states to an optimal action
        Note: epsilon is the error tolerance: you should stop value iteration when
        all of the values change by less than epsilon.
        The ValueIteration class is a subclass of util.MDPAlgorithm (see util.py).
        """
        mdp.computeStates()
        def computeQ(mdp, V, state, action):
            # Return Q(state, action) based on V(state).
            return sum(prob * (reward + mdp.discount() * V[newState]) \
                            for newState, prob, reward in mdp.succAndProbReward(state, action))

        def computeOptimalPolicy(mdp, V):
            # Return the optimal policy given the values V.
            pi = {}
            for state in mdp.states:
                pi[state] = max((computeQ(mdp, V, state, action), action) for action in mdp.actions(state))[1]
            return pi
        V = defaultdict(float)  # state -> value of state
        # Implement the main loop of Asynchronous Value Iteration Here:
        done = False
        Vl = {} # V'
        Vl = defaultdict(float)
        for state in mdp.states:
            V[state] = 0.0
        while not done:
            for state in mdp.states:
                Vl[state] = -math.inf # V'
            for state in mdp.states:
                for action in mdp.actions(state):
                    Q = 0
                    R = 0
                    # Successor states and probs and rewards
                    for ss, p, r in mdp.succAndProbReward(state, action):
                        Q += p*V[ss]
                        # if there is more than 1 possible reward, we can
                        # pick any of them because they are all 0

                        # the only cases where the reward is not zero are when
                        # the list of succAndProbReward has only 1 element
                        # e.g when action is quit or peek
                        R = r
                    Q = Q + R
                    if Q > Vl[state]:
                        Vl[state] = Q
            done = True
            for state in mdp.states: # V <- V'
                # takes epsilon into consideration
                if abs(V[state] - Vl[state]) >= epsilon:
                    done = False
                    V[state] = Vl[state]
        # END_YOUR_CODE

        # Extract the optimal policy now
        pi = computeOptimalPolicy(mdp, V)
        # print("ValueIteration: %d iterations" % numIters)
        self.pi = pi
        self.V = V

# First MDP
MDP1 = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=10, peekCost=1)

# Second MDP
MDP2 = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=15, peekCost=1)

def peekingMDP():
    """
    Return an instance of BlackjackMDP where peeking is the
    optimal action for at least 10% of the states.
    """
    # BEGIN_YOUR_CODE
    threshold = 20
    peekCost = 1
    cardValues = [5, 100]
    multiplicity = 10

    return BlackjackMDP(cardValues, multiplicity, threshold, peekCost)
    # END_YOUR_CODE


# **********************************************************
# **                    PART 03 Q-Learning                **
# **********************************************************

class QLearningAlgorithm(util.RLAlgorithm):
    """
    Performs Q-learning.  Read util.RLAlgorithm for more information.
    actions: a function that takes a state and returns a list of actions.
    discount: a number between 0 and 1, which determines the discount factor
    featureExtractor: a function that takes a state and action and returns a
    list of (feature name, feature value) pairs.
    explorationProb: the epsilon value indicating how frequently the policy
    returns a random action
    """
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.numIters = 0

    def getQ(self, state, action):
        """
         Return the Q function associated with the weights and features
        """
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    def getAction(self, state):
        """
        Produce an action given a state, using the epsilon-greedy algorithm: with probability
        |explorationProb|, take a random action.
        """
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        return max((self.getQ(state, action), action) for action in self.actions(state))[1]

    def getStepSize(self):
        """
        Return the step size to update the weights.
        """
        return 1.0 / math.sqrt(self.numIters)

    def incorporateFeedback(self, state, action, reward, newState):
        """
         We will call this function with (s, a, r, s'), which you should use to update |weights|.
         You should update the weights using self.getStepSize(); use
         self.getQ() to compute the current estimate of the parameters.

         HINT: Remember to check if s is a terminal state and s' None.
        """
        # BEGIN_YOUR_CODE
        cur_Q = self.getQ(state, action)
        if newState != None:
            for f, v in self.featureExtractor(state, action):
                self.weights[f] += self.getStepSize()
        # END_YOUR_CODE

def identityFeatureExtractor(state, action):
    """
    Return a single-element list containing a binary (indicator) feature
    for the existence of the (state, action) pair.  Provides no generalization.
    """
    featureKey = (state, action)
    featureValue = 1
    return [(featureKey, featureValue)]

# Large test case
largeMDP = BlackjackMDP(cardValues=[1, 3, 5, 8, 10], multiplicity=3, threshold=40, peekCost=1)

# **********************************************************
# **        PART 03-01 Features for Q-Learning             **
# **********************************************************

def blackjackFeatureExtractor(state, action):
    """
    You should return a list of (feature key, feature value) pairs.
    (See identityFeatureExtractor() above for a simple example.)
    """
    # BEGIN_YOUR_CODE
    raise Exception("Not implemented yet")
    # END_YOUR_CODE

# def main():
#     smallMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2,
#                                    threshold=15, peekCost=1)
#     preEmptyState = (11, None, (1,0))
#     tests = [
#         ([((12, None, None), 1, 12)], smallMDP, preEmptyState, 'Take'),
#         ([((5, None, (2, 1)), 1, 0)], smallMDP, (0, 1, (2, 2)), 'Take')
#     ]
#     for gold, mdp, state, action in tests:
#         if  gold == mdp.succAndProbReward(state, action):
#             print('yeeeeeah')
#         else:
#             print('oh no')
#             print(gold)
# main()
