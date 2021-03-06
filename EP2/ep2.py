"""
    AO PREENCHER ESSE CABECALHO COM O MEU NOME E O MEU NUMERO USP, DECLARO
    QUE SOU A UNICA PESSOA AUTORA E RESPONSAVEL POR ESSE PROGRAMA.
    TODAS AS PARTES ORIGINAIS DESSE EXERCICIO PROGRAMA (EP) FORAM
    DESENVOLVIDAS E IMPLEMENTADAS POR MIM SEGUINDO AS INSTRUCOES DESSE EP E,
    PORTANTO, NAO CONSTITUEM ATO DE DESONESTIDADE ACADEMICA, FALTA DE ETICA
    OU PLAGIO.
    DECLARO TAMBEM QUE SOU A PESSOA RESPONSAVEL POR TODAS AS COPIAS DESSE
    PROGRAMA E QUE NAO DISTRIBUI OU FACILITEI A SUA DISTRIBUICAO. ESTOU
    CIENTE QUE OS CASOS DE PLAGIO E DESONESTIDADE ACADEMICA SERAO TRATADOS
    SEGUNDO OS CRITERIOS DIVULGADOS NA PAGINA DA DISCIPLINA.
    ENTENDO QUE EPS SEM ASSINATURA NAO SERAO CORRIGIDOS E, AINDA ASSIM,
    PODERAO SER PUNIDOS POR DESONESTIDADE ACADEMICA.

    Nome: Henrique Cerquinho
    NUSP: 9793700

    Referencias: Com excecao das rotinas fornecidas no enunciado e em sala
    de aula, caso voce tenha utilizado alguma referencia, liste-as abaixo
    para que o seu programa nao seja considerado plagio ou irregular.

    Exemplo:
    - O algoritmo Quicksort foi baseado em:
    https://pt.wikipedia.org/wiki/Quicksort
    http://www.ime.usp.br/~pf/algoritmos/aulas/quick.html
"""
import copy
import random
import util
import itertools

# **********************************************************
# **                    PART 00 START                     **
# **********************************************************
class RandomAgent(util.Agent):
    """ Implements an agent that chooses a random action """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid = None
        self.grid_height = None
        self.grid_width = None

    def __state_from_perception(self, perception):
        """ Private method to help to convert a perception into a state """
        grid, remaining_gas = perception
        self.grid = grid
        self.grid_height = len(self.grid)
        self.grid_width = len(self.grid[0])
        # Car parked on the gas station
        player_values = [self.player_number, self.player_number+7]
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] in player_values:
                    return ((i, j), remaining_gas)
        return None

    def __process_state(self, state):
        """ Private method that process a given state returning relevant info
        """
        agent_pos, remaining_gas = state
        i, j = agent_pos
        grid_number = self.grid[i][j]
        if grid_number not in [1, 2, 8, 9]:
            raise ValueError("There is no player at position: ({0},{1})".format(i, j))
        # Fix number in case car is inside gas station
        if grid_number > 2:
            player_number = grid_number - 7
        else:
            player_number = grid_number
        if player_number == 1:
            obstacles = [2, 5, 9]
        else:
            obstacles = [1, 5, 8]
        full_info = (agent_pos, player_number, obstacles, remaining_gas)
        return full_info

    def actions(self, state):
        """ Returns a list of valid actions for a given state,
        this time taking into consideration obstacles and grid size """
        ag_pos, pl_number, obstacles, rem_gas = self.__process_state(state)
        i, j = ag_pos
        gas_station = pl_number + 7

        valid = []
        if rem_gas > 0:
            if i-1 >= 0 and self.grid[i-1][j] not in obstacles:
                valid.append('UP')
            if j+1 < self.grid_width and self.grid[i][j+1] not in obstacles:
                valid.append('RIGHT')
            if i+1 < self.grid_height and self.grid[i+1][j] not in obstacles:
                valid.append('DOWN')
            if j-1 >= 0 and self.grid[i][j-1] not in obstacles:
                valid.append('LEFT')
        if self.grid[i][j] == gas_station:
            valid.append('REFILL')
        valid.append('STOP')  # STOP is always a valid action
        return valid

    def get_action(self, perception):
        """ Chooses a random action from the list of valid actions """
        state = self.__state_from_perception(perception)
        return random.choice(self.actions(state))


# **********************************************************
# **                    PART 00 END                       **
# **********************************************************

# **********************************************************
# **                    PART 01 START                     **
# **********************************************************
class CollectAllAgent(util.Agent):
    def __init__(self, **kwargs):
        """
        As stated before, all information that will be passed during the
        initialization is packed in the kwargs and, because of that, unless
        you decided to implement fancy attributes here, you can safely
        pass the kwargs dictionary directly to the superclass constructor.
        For pedagogical reasons, we decided that we will instatiate additional
        attributes here that will be later set via start_agent method.
        """
        super().__init__(**kwargs)
        self.problem_reference = CollectAllProblem
        self.problem = None
        self.goal = 0


    def __state_from_perception(self, perception):
        """ Private method to help to convert a perception into a state

        This is a helper method that converts a perception passed from the
        environment into a state to be used in the search problem.

        :param perception: The perception your agent acquires from the
            environment.
        :type perception: Problem dependent (for this programming assignment a
            tuple with the grid matrix and the remaining fuel for your agent)
        :return: A problem state according with your conception of problem.
            (E.g. for GetClosestPersonOrRefillProblem, we chose a state as a
            tuple with the agent coordinates and its remaining fuel)
            For this agent, the state will also have the sequence in which
            he will pick up each person, so that will be used in the heuristic.
        """
        grid, remaining_gas = perception
        player_values = [self.player_number, self.player_number+7]
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] in player_values:
                    return ((i, j), remaining_gas)
        return None


    def start_agent(self, perception, problem, **kwargs):
        """ Initialize all non-default attributes in the agent

        This is a helper method to allow the instantiation of all non-default
        attributes from this class.
        In this particular case, we are instantiating a search problem
        according with the perception and the specs provided.
        """
        self.initial_state = self.__state_from_perception(perception)
        grid, _ = perception
        new_grid = copy.deepcopy(grid)
        self.problem = problem(new_grid, self.initial_state, **kwargs)


    def heuristic(self, node):
        """ Heuristic to be used by the A* algorithm
        Here, we have that state[2] is the sequence for picking up people.
        That is, seq[0] is the first person to be picked up, seq[1] is the
        second, etc. Therefore, the heuristic will be the manhattan distance
        between the agent and seq[0] everytime, given that seq is updated
        everytime a person is picked up.
        """
        seq = node.state[2]
        pos = node.state[0]
        if len(seq) > 0:
            return abs(pos[0]-seq[0][0])+abs(pos[1]-seq[0][1])
        return util.INT_INFTY


    def get_action(self, perception):
        """ This is the main method for all your agents

        Along with the __init__, you must at least implement this method in
        all your agents to make them work properly.

        This method receives a perception from the environment and returns
        an action after performing the A* search with manhattan_distance as
        heuristics.
        """
        state = self.__state_from_perception(perception)
        i,j = state[0]
        grid, _ = perception

        # if gas station and tank not full, refill
        if grid[i][j] == self.player_number+7 and state[1] < self.tank_capacity:
            return 'REFILL'

        self.start_agent(perception, self.problem_reference,
                         tank_capacity=self.tank_capacity)
        node = util.a_star(self.problem, self.heuristic)
        if not node:  # Search did not find any action
            return 'STOP'
        action = node.action
        last_action = None
        while node.parent is not None:
            node = node.parent
            last_action = action
            action = node.action
        return last_action


class CollectAllProblem(util.Problem):
    """ Class that implements the problem for the GetClosestPersonOrRefillAgent

    For this particular agent it performs an A* search with manhattan distance
    as heuristic.

    Mostrly copied from the GetClosestPersonOrRefillProblem
    """
    def __init__(self, grid, initial_state, **kwargs):
        self.grid = copy.deepcopy(grid)
        self.grid_height = len(self.grid)
        self.grid_width = len(self.grid[0])
        self.people_position = self.__all_people()
        self.best_seq = self.__process_sequence(initial_state[0])
        self.init_state = (initial_state[0], initial_state[1], self.best_seq)
        self.tank_capacity = kwargs.get('tank_capacity', util.INT_INFTY)
        self.max_depth = kwargs.get('max_depth', util.MAX_DEPTH)


    def __process_sequence(self, pos):
        """ Here we will find out the order in which we have to pick up
        the people. This order will be used in the heuristic function """
        goals = self.get_people_position()
        goals_list = []
        # This will be a 'dictionary matrix', containing the distances
        # between every pair of person
        pair_dists = {}

        # Floyd Warshall like search for each person
        for person1 in goals:
            print(person1)
            goals_list.append(person1)
            pair_dists[person1] = {}
            for person2 in goals:
                if person1 != person2:
                    pair_dists[person1][person2] = abs(person1[0]-person2[0])+abs(person1[1]-person2[1])

        # for every permutation of the sequence of people, we'll check which
        # one has the smallest distance sum
        permutations = list(itertools.permutations(goals_list))
        best = util.INT_INFTY
        for seq in permutations:
            # distance from the agent to first person in the current sequence
            dist_to_first = abs(pos[0]-seq[0][0])+abs(pos[1]-seq[0][1])
            seq_dist = 0
            # rest of the distance
            for i in range(len(seq) - 1):
                seq_dist += pair_dists[seq[i]][seq[i+1]]
            if dist_to_first + seq_dist < best:
                best = dist_to_first + seq_dist
                best_seq = seq
        return best_seq


    def __process_state(self, state):
        """ Private method that process a given state returning relevant info

        Helper method that receives a state and returns four important info
        from that state in the following order:
            - A tuple of integers (i,j) with the player position on the grid
            - An integer with the player_number
            - A list with the obstacles for that player_number
            - An integer with the remaining fuel the agent have

        :param state: A tuple with agent position and remaining fuel
        :type state: <class 'tuple'>
        :return full_info: A tuple with the four info described above
        :rtype: <class 'tuple'>

        Here, we also return the sequence processed above.
        """
        agent_pos, remaining_gas, seq = state
        i, j = agent_pos
        grid_number = self.grid[i][j]
        if grid_number not in [1, 2, 8, 9]:
            raise ValueError("There is no player at position: ({0},{1})".format(i, j))
        # Fix number in case car is inside gas station
        if grid_number > 2:
            player_number = grid_number - 7
        else:
            player_number = grid_number
        if player_number == 1:
            obstacles = [2, 5, 9]
        else:
            obstacles = [1, 5, 8]
        full_info = (agent_pos, player_number, obstacles, remaining_gas, seq)
        return full_info


    def initial_state(self):
        """ Gets the initial state """
        return self.init_state


    def get_people_position(self):
        """ Auxiliary method that returns the dictionary of people positions """
        return self.people_position


    def get_sequence(self):
        """ Auxiliary method that returns the sequence for pickung up people """
        return self.best_seq


    def __all_people(self):
        """ Private method that find all people in the grid returning a dict

        Private method to help the identification of goal_state.
        It find all people inside the grid and returns a dict with indexed
        by the people coordinate whose value is the people code in the grid.

        :return people_pos: A dictionary with (i,j) coord as index and
            people code number as value
        :rtype: <class 'dict'>
        """
        people_pos = {}
        people_numbers = [3, 6, 7]
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] in people_numbers:
                    people_pos[(i, j)] = self.grid[i][j]
        return people_pos


    def actions(self, state):
        """ Returns a list of valid actions for a given state """
        ag_pos, pl_number, obstacles, rem_gas, _ = self.__process_state(state)
        i, j = ag_pos
        gas_station = pl_number + 7

        valid = []
        if rem_gas > 0:
            if i-1 >= 0 and self.grid[i-1][j] not in obstacles:
                valid.append('UP')
            if j+1 < self.grid_width and self.grid[i][j+1] not in obstacles:
                valid.append('RIGHT')
            if i+1 < self.grid_height and self.grid[i+1][j] not in obstacles:
                valid.append('DOWN')
            if j-1 >= 0 and self.grid[i][j-1] not in obstacles:
                valid.append('LEFT')
        if self.grid[i][j] == gas_station:
            valid.append('REFILL')
        valid.append('STOP')  # STOP is always a valid action
        return valid


    def next_state(self, state, action):
        """ Implements the transition function T(s,a) """
        ag_pos, player_number, _, remaining_gas, seq = self.__process_state(state)
        new_seq = seq
        i, j = ag_pos
        people_numbers = [3, 6, 7]
        aux = {'UP'    : (i-1, j),
               'DOWN'  : (i+1, j),
               'LEFT'  : (i, j-1),
               'RIGHT' : (i, j+1),
               'STOP'  : (i, j),
               'REFILL': (i, j)}

        # Trying to perform invalid action, stay where there and spend fuel
        if action not in self.actions(state):
            return (aux['STOP'], remaining_gas - self.cost(state, action), new_seq)
        new_i, new_j = aux[action]

        if action == 'REFILL':
            if remaining_gas + util.DEFAULT_REFILL > self.tank_capacity:
                self.grid[new_i][new_j] = player_number + 7
                return (aux['REFILL'], self.tank_capacity, new_seq)
            else:
                self.grid[new_i][new_j] = player_number + 7
                return (aux['REFILL'], remaining_gas + util.DEFAULT_REFILL, new_seq)
        if self.grid[new_i][new_j] == 4:  # Agent going to a gas station
            self.grid[new_i][new_j] = player_number + 7
        else:
            if self.grid[new_i][new_j] in people_numbers or (len(seq) > 0 and (new_i, new_j) == seq[0]):
                new_seq = []
                for i in range(1,len(seq)):
                    new_seq.append(seq[i])
                new_seq = tuple(new_seq)
            self.grid[new_i][new_j] = player_number
        return (aux[action], remaining_gas - self.cost(state, action), new_seq)


    def is_goal_state(self, state):
        """ Is goal if the current position equals the one in the start of
        the sequence.
        """
        pos = state[0]
        if pos == self.get_sequence()[0]:
            return True
        return False


    def cost(self, state, action):
        """ Implements the step cost function

        Invalid actions have cost of 1
        STOP and REFILL has cost of 0 and
        Any other valid action has cost of 1
        """
        # Action is a invalid action, has cost of one gas unit
        if action not in self.actions(state):
            return 1
        # Action is valid, but it is a STOP or REFILL action, no cost
        if action in ['STOP', 'REFILL']:
            return 0
        return 1  # All other valid actions has cost 1


# **********************************************************
# **                    PART 01 END                       **
# **********************************************************

# **********************************************************
# **                    PART 02 START                     **
# **********************************************************

class AlphaBetaAgent(util.Agent):
    """
    The AlphaBetaAgent class is a subclass of Agent that implements a specific
    adversarial agent that performs an Alpha/Beta search with cuttoff, where
    the cutoff test is based on the max_depth parameter.
    """
    def __init__(self, **kwargs):
        """
        Like some other agents we provided, here we also initialize the
        reference to the problem and its instantiation that will be set
        by get_action.
        """
        super().__init__(**kwargs)
        self.problem_reference = AlphaBetaAgentProblem
        self.problem = None


    def __perception_to_state(self, perception):
        """ Converts a perception into a start to be used by the search

         We decided that a state for this agent could be a tuple with:
            - The game grid
            - The current agent
            - The remaining fuel for agent1
            - The remaining fuel for agent2
            - The bonus for people collected by agent1 during the search
            - The bonus for people collected by agent2 during the search

        Since our perception does not provide the remaining fuel for
        agent2, we chose to consider that the adversarial has the same
        amount of fuel that our agent has. (We could instead suppose that
        the opponent starts always with the full tank, feel free to try it)
        """
        grid, remaining_gas = perception
        state = (grid, self.player_number, remaining_gas, remaining_gas, 0, 0)
        return state


    def get_action(self, perception):
        """ Receives a perception and returns an action after search """
        self.initial_state = self.__perception_to_state(perception)
        self.problem = self.problem_reference(state=self.initial_state,
                                              max_depth=self.max_depth)
        action = self.problem.alphabeta_search(self.initial_state)
        if not action:  # Somehow minimax did not found a solution
            return 'STOP'
        else:
            return action


class AlphaBetaAgentProblem(util.Problem):
    """ Implements the problem class for AlphaBetaAgent """
    def __init__(self, state, **kwargs):
        self.__player = kwargs.get('starting_player', 1)
        self.st_gas = kwargs.get('tank_capacity', util.INT_INFTY)
        self.max_depth = kwargs.get('max_depth', util.MAX_DEPTH)
        self.cutoff_test = kwargs.get('cutoff_test', self.cutoff_by_depth)
        self.init_state = state
        self.eval_fn = kwargs.get('eval_fn', self.my_better_evaluation_function)


    def initial_state(self):
        return self.init_state


    def cutoff_by_depth(self, _, depth):
        """ Implements the heuristics for cutoff

        .. warning::
            You do not have to change this method, do it at your own risk
        """
        if depth > self.max_depth:
            return True
        return False


    @staticmethod
    def __player_pos(state):
        """ Helper method to find the coordinates of player position """
        grid, player, _, _, _, _ = state
        if player == 2:
            current_player = [2, 9]
        else:
            current_player = [1, 8]

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] in current_player:
                    return (i, j)
        return None


    def actions(self, state):
        """ Returns a list with all valid actions from that state """
        grid, player, agent1gas, agent2gas, _, _ = state
        player_pos = self.__player_pos(state)
        i, j = player_pos

        if player == 1:
            obstacles = [2, 5, 9]
            inside_gas_station = 8
            remaining_gas = agent1gas
        else:
            obstacles = [1, 5, 8]
            inside_gas_station = 9
            remaining_gas = agent2gas

        valid = []
        if remaining_gas > 0:
            if i+1 < len(grid) and grid[i+1][j] not in obstacles:
                valid.append('DOWN')
            if i-1 >= 0 and grid[i-1][j] not in obstacles:
                valid.append('UP')
            if j-1 >= 0 and grid[i][j-1] not in obstacles:
                valid.append('LEFT')
            if j+1 < len(grid[0]) and grid[i][j+1] not in obstacles:
                valid.append('RIGHT')
        if grid[i][j] == inside_gas_station:
            valid.append('REFILL')
        valid.append('STOP')  # STOP is always a valid action
        return valid


    def next_state(self, state, action):
        """ Implements the transition function T(s,a) """
        # agent_N_remaining_gas = aNg and agent_N_people_bonus = aNp
        grid, player, a1g, a2g, a1p, a2p = state
        new_grid = copy.deepcopy(grid)
        if player == 1:
            next_player = 2
        else:
            next_player = 1
        if action not in self.actions(state):  # Tried invalid action
            if player == 1:
                return (new_grid, next_player, a1g-1, a2g, a1p, a2p)
            else:
                return (new_grid, next_player, a1g, a2g-1, a1p, a2p)

        player_pos = self.__player_pos(state)
        i, j = player_pos

        aux = {'UP'    : [i-1, j],
               'DOWN'  : [i+1, j],
               'LEFT'  : [i, j-1],
               'RIGHT' : [i, j+1],
               'STOP'  : [i, j],
               'REFILL': [i, j]}

        if action == 'STOP':
            if player == 1:
                return (new_grid, 2, a1g, a2g, a1p, a2p)
            else:
                return (new_grid, 1, a1g, a2g, a1p, a2p)

        if action == 'REFILL':
            if player == 1:
                # Refill or max
                if a1g + util.DEFAULT_REFILL < self.st_gas:
                    a1g += util.DEFAULT_REFILL
                else:
                    a1g = self.st_gas
                return (new_grid, 2, a1g, a2g, a1p, a2p)
            else:
                if a2g + util.DEFAULT_REFILL < self.st_gas:
                    a2g += util.DEFAULT_REFILL
                else:
                    a2g = self.st_gas
                return (new_grid, 1, a1g, a2g, a1p, a2p)


        actual_cell = new_grid[i][j]
        future_cell = new_grid[aux[action][0]][aux[action][1]]
        # Not STOP nor REFILL, process cell that taxi is leaving
        if actual_cell in [8, 9]:  # Leaving a gas station
            new_grid[i][j] = 4  # Revert to gas station
        else:
            new_grid[i][j] = 0  # Not leaving gas, just empty cell

        # Process cell that taxi will arrive
        # Deal with complicated cases first, taxi going to gas station
        if future_cell == 4:
            new_grid[aux[action][0]][aux[action][1]] = player + 7
            if player == 1:
                return (new_grid, 2, a1g-1, a2g, a1p, a2p)
            else:
                return (new_grid, 1, a1g, a2g-1, a1p, a2p)
        # Other cases taxi will fill that cell and only check if got people
        new_grid[aux[action][0]][aux[action][1]] = player
        if future_cell == 3:  # Got random person
            if player == 1:
                a1p += util.STUDENT_BONUS
            else:
                a2p += util.STUDENT_BONUS
        elif future_cell == 6:  # Got a professor
            if player == 1:
                a1p += util.PROFESSOR_BONUS
            else:
                a2p += util.PROFESSOR_BONUS
        elif future_cell == 7:  # Got a monitor
            if player == 1:
                a1p += util.MONITOR_BONUS
            else:
                a2p += util.MONITOR_BONUS
        # All possible bonus computed, just update fuel/gas and return
        if player == 1:
            return (new_grid, 2, a1g-1, a2g, a1p, a2p)
        else:
            return (new_grid, 1, a1g, a2g-1, a1p, a2p)


    def __inside_gas_station(self, state):
        """ Auxiliary method to find if a player is inside a gas station """
        grid, _, _, _, _, _ = state
        player_pos = self.__player_pos(state)
        i, j = player_pos
        if grid[i][j] > 2:
            return True
        return False


    def is_goal_state(self, state):
        """ Check if state is goal

        Goal state reached in two ways:
            - No fuel for both agents AND agents not parked in gas station
            - All people collected
        """
        # Checking fuel and gas station first
        grid, _, a1g, a2g, a1p, a2p = state
        if a1g == 0 and a2g == 0:
            a1_in_gas = self.__inside_gas_station((grid, 1, a1g, a2g, a1p, a2p))
            a2_in_gas = self.__inside_gas_station((grid, 2, a1g, a2g, a1p, a2p))
            if not a1_in_gas and not a2_in_gas:  # Fuel ended and neither in gas
                return True
        # Checking for people collected
        people_codes = [3, 6, 7]  # Student, Professor and Monitor
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] in people_codes:
                    return False
        # Outside the for, no person left so it is a goal
        return True


    def cost(self, state, action):
        # This is not a redundant check because REFILL could be invalid action
        if action not in self.actions(state):
            return 1
        if action in ['REFILL', 'STOP']:
            return 0
        return 1


    @staticmethod
    def utility(state, player=1):
        """ Computes the utility when the agent reached a goal state

        .. notes::
            You should not think about the parameter player. The checking of
            which player we are computing the score is JUST for debug/autograder
            use ONLY!
            For your programming assignment you ALWAYS compute the score
            based on player=1
        """
        _, _, _, _, a1p, a2p = state
        if player == 1:
            return a1p
        else:
            return a2p

    @staticmethod
    def evaluation_function(state, player=1):
        """ Evaluate the state during the pruning

        Naive evaluation function that considers state value equal to the
        utility of that state at the goal. (end game score)
        This is not a good evaluation function because, for instance, the fact
        that player 1 did not collected any person while we call the pruning
        (meaning that its score so far is 0) does not means that this score
        will remain 0 until the end of the game.

        Considers the following situation with pruning at depth 1:
        ---------------------
        |   | 5 |   | 5 | 3 |
        ---------------------
        |   | 5 |   | 5 | 3 |
        ---------------------
        |   | 5 | 2 | 5 | 3 |
        ---------------------
        | 3 | 1 |   |   | 7 |
        ---------------------
        |   |   |   |   |   |
        ---------------------
        Actions:
        Game1: player1:LEFT,  player2:DOWN -> evaluation return 1
        Game2: player1:RIGHT, player2:UP   -> evaluation return 0
        Considering that both players play optimally after the first turn, by
        going LEFT player one just collect one student and by going RIGHT it
        collect a monitor and 3 students. Clearly going RIGHT should have
        a better evaluation than going LEFT, but that does not occurs when
        using the utility as evaluation.

        .. notes::
            You should not think about the parameter player. The checking of
            which player we are computing the evaluation is JUST for
            debug/autograder use ONLY!
            For your programming assignment you ALWAYS compute the score
            based on player=1
        """
        _, _, _, _, a1p, a2p = state
        if player == 1:
            return a1p
        else:
            return a2p


    def my_better_evaluation_function(self, state, player=1):
        """ Here you must implement your own evaluation function """
        grid, _, a1g, a2g, a1p, a2p = state
        pos = (-1,-1)
        value = 0
        # finds agent in the grid
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == player:
                    pos = (i,j)

        people_codes = [3, 6, 7]
        # extra points if got the last person
        empty = 1
        # gets the distance to every person, and sums up 1/(each one of the distances)
        # that way, the closest you are to a bigger group of people,
        # the higher the value.

        # also returns the current points of the player, so there is a motivation
        # to pick people up

        # lastly, returns a bonus if the board is empty, motivating the agent
        # to finish the game
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] in people_codes:
                    empty = 0
                    dist = abs(i-pos[0])+abs(j-pos[1])
                    value += 1/(dist)
        return value + a1p*1.1 + empty*10

    def manhattan_distance(self, node):
        """ Heuristic to be used by the A* algorithm """
        goals = self.problem.get_people_position()
        state = node.state[0]
        best_distance = util.INT_INFTY
        for people in goals:
            manhattan = abs(state[0]-people[0])+abs(state[1]-people[1])
            if manhattan < best_distance:
                best_distance = manhattan
        return best_distance

    def alphabeta_search(self, state, depth=0):
        """ Alpha/Beta search using cutoff_test and eval_fn """

        alpha = -float('inf')
        beta = float('inf')
        best_action = None
        for action in self.actions(state):
            value = self.min_value(self.next_state(state, action), alpha,
                                   beta, depth)
            if value > alpha:
                alpha = value
                best_action = action
        return best_action


    def max_value(self, state, alpha, beta, depth):
        """ The Alpha/Beta processing for max internal nodes """
        if self.cutoff_test(state, depth):
            return self.eval_fn(state)
        value = -float('inf')
        for action in self.actions(state):
            value = max(value, self.min_value(self.next_state(state, action),
                                              alpha, beta, depth))
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value


    def min_value(self, state, alpha, beta, depth):
        """ The Alpha/Beta processing for min internal nodes """
        if self.cutoff_test(state, depth):
            return self.eval_fn(state)
        value = float('inf')
        for action in self.actions(state):
            value = min(value, self.max_value(self.next_state(state, action),
                                              alpha, beta, depth + 1))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value

# **********************************************************
# **                    PART 02 END                       **
# **********************************************************

# IMPORTANT: You should not need to change anything from this point.
# Do it at your own risk

class GetClosestPersonOrRefillAgent(util.Agent):
    """ Agent Class that implements a planning agent

    The GetClosestPersonOrRefill class is a subclass of Agent that implements a
    specific agent whose objective is to collect the closest available person
    or refuelling, by using A* search with manhattan distance as heuristic.

    On each step this agent perform a new A* search until the problem reached
    a goal state. Also, it always process the actions in the following order:
    'UP', 'RIGHT', 'DOWN', 'LEFT', 'REFILL', 'STOP' and in case of ties when
    computing the heuristic, it uses a FIFO tie-breaker heuristic to pop from
    the priority queue.

    .. notes::
        The code below is provided to you as a guide and it is completely
        functional. Since you will only use it to familiarize yourself with
        the interface, you are welcome to change it in any way you see fit,
        as long as you do not change the type of the ``state'' argument
        for get_action method and start_agent method.
        We cannot ensure that the controller nor the view will continue to
        work if you change those.
    """
    def __init__(self, **kwargs):
        """
        As stated before, all information that will be passed during the
        initialization is packed in the kwargs and, because of that, unless
        you decided to implement fancy attributes here, you can safely
        pass the kwargs dictionary directly to the superclass constructor.
        For pedagogical reasons, we decided that we will instatiate additional
        attributes here that will be later set via start_agent method.
        """
        super().__init__(**kwargs)
        self.problem_reference = GetClosestPersonOrRefillProblem
        self.problem = None


    def __state_from_perception(self, perception):
        """ Private method to help to convert a perception into a state

        This is a helper method that converts a perception passed from the
        environment into a state to be used in the search problem.

        :param perception: The perception your agent acquires from the
            environment.
        :type perception: Problem dependent (for this programming assignment a
            tuple with the grid matrix and the remaining fuel for your agent)
        :return: A problem state according with your conception of problem.
            (E.g. for GetClosestPersonOrRefillProblem, we chose a state as a
            tuple with the agent coordinates and its remaining fuel)
        """
        grid, remaining_gas = perception
        # Car and car parked on the gas station
        player_values = [self.player_number, self.player_number+7]
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] in player_values:
                    return ((i, j), remaining_gas)
        return None


    def start_agent(self, perception, problem, **kwargs):
        """ Initialize all non-default attributes in the agent

        This is a helper method to allow the instantiation of all non-default
        attributes from this class.
        In this particular case, we are instantiating a search problem
        according with the perception and the specs provided.
        """
        self.initial_state = self.__state_from_perception(perception)
        grid, _ = perception
        new_grid = copy.deepcopy(grid)
        self.problem = problem(new_grid, self.initial_state, **kwargs)


    def manhattan_distance(self, node):
        """ Heuristic to be used by the A* algorithm """
        goals = self.problem.get_people_position()
        state = node.state[0]
        best_distance = util.INT_INFTY
        for people in goals:
            manhattan = abs(state[0]-people[0])+abs(state[1]-people[1])
            if manhattan < best_distance:
                best_distance = manhattan
        return best_distance


    def get_action(self, perception):
        """ This is the main method for all your agents

        Along with the __init__, you must at least implement this method in
        all your agents to make them work properly.

        This method receives a perception from the environment and returns
        an action after performing the A* search with manhattan_distance as
        heuristics.
        """
        self.start_agent(perception, self.problem_reference,
                         tank_capacity=self.tank_capacity)
        node = util.a_star(self.problem, self.manhattan_distance)
        if not node:  # Search did not find any action
            return 'STOP'
        action = node.action
        last_action = None
        while node.parent is not None:
            node = node.parent
            last_action = action
            action = node.action
        return last_action


class GetClosestPersonOrRefillProblem(util.Problem):
    """ Class that implements the problem for the GetClosestPersonOrRefillAgent

    For this particular agent it performs an A* search with manhattan distance
    as heuristic.
    """
    def __init__(self, grid, initial_state, **kwargs):
        self.grid = copy.deepcopy(grid)
        self.init_state = initial_state
        self.grid_height = len(self.grid)
        self.grid_width = len(self.grid[0])
        self.people_position = self.__all_people()
        self.tank_capacity = kwargs.get('tank_capacity', util.INT_INFTY)
        self.max_depth = kwargs.get('max_depth', util.MAX_DEPTH)


    def __process_state(self, state):
        """ Private method that process a given state returning relevant info

        Helper method that receives a state and returns four important info
        from that state in the following order:
            - A tuple of integers (i,j) with the player position on the grid
            - An integer with the player_number
            - A list with the obstacles for that player_number
            - An integer with the remaining fuel the agent have

        :param state: A tuple with agent position and remaining fuel
        :type state: <class 'tuple'>
        :return full_info: A tuple with the four info described above
        :rtype: <class 'tuple'>
        """
        agent_pos, remaining_gas = state
        i, j = agent_pos
        grid_number = self.grid[i][j]
        if grid_number not in [1, 2, 8, 9]:
            raise ValueError("There is no player at position: ({0},{1})".format(i, j))
        # Fix number in case car is inside gas station
        if grid_number > 2:
            player_number = grid_number - 7
        else:
            player_number = grid_number
        if player_number == 1:
            obstacles = [2, 5, 9]
        else:
            obstacles = [1, 5, 8]
        full_info = (agent_pos, player_number, obstacles, remaining_gas)
        return full_info


    def initial_state(self):
        """ Gets the initial state """
        return self.init_state


    def get_people_position(self):
        """ Auxiliary method that returns the dictionary of people positions """
        return self.people_position


    def __all_people(self):
        """ Private method that find all people in the grid returning a dict

        Private method to help the identification of goal_state.
        It find all people inside the grid and returns a dict with indexed
        by the people coordinate whose value is the people code in the grid.

        :return people_pos: A dictionary with (i,j) coord as index and
            people code number as value
        :rtype: <class 'dict'>
        """
        people_pos = {}
        people_numbers = [3, 6, 7]
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] in people_numbers:
                    people_pos[(i, j)] = self.grid[i][j]
        return people_pos


    def actions(self, state):
        """ Returns a list of valid actions for a given state """
        ag_pos, pl_number, obstacles, rem_gas = self.__process_state(state)
        i, j = ag_pos
        gas_station = pl_number + 7

        valid = []
        if rem_gas > 0:
            if i-1 >= 0 and self.grid[i-1][j] not in obstacles:
                valid.append('UP')
            if j+1 < self.grid_width and self.grid[i][j+1] not in obstacles:
                valid.append('RIGHT')
            if i+1 < self.grid_height and self.grid[i+1][j] not in obstacles:
                valid.append('DOWN')
            if j-1 >= 0 and self.grid[i][j-1] not in obstacles:
                valid.append('LEFT')
        if self.grid[i][j] == gas_station:
            valid.append('REFILL')
        valid.append('STOP')  # STOP is always a valid action
        return valid


    def next_state(self, state, action):
        """ Implements the transition function T(s,a) """
        ag_pos, player_number, _, remaining_gas = self.__process_state(state)
        i, j = ag_pos
        aux = {'UP'    : (i-1, j),
               'DOWN'  : (i+1, j),
               'LEFT'  : (i, j-1),
               'RIGHT' : (i, j+1),
               'STOP'  : (i, j),
               'REFILL': (i, j)}

        # Trying to perform invalid action, stay where there and spend fuel
        if action not in self.actions(state):
            return (aux['STOP'], remaining_gas - self.cost(state, action))
        new_i, new_j = aux[action]
        if action == 'REFILL':
            if remaining_gas + util.DEFAULT_REFILL > self.tank_capacity:
                self.grid[new_i][new_j] = player_number + 7
                return (aux['REFILL'], self.tank_capacity)
            else:
                self.grid[new_i][new_j] = player_number + 7
                return (aux['REFILL'], remaining_gas + util.DEFAULT_REFILL)
        if self.grid[new_i][new_j] == 4:  # Agent going to a gas station
            self.grid[new_i][new_j] = player_number + 7
        else:
            self.grid[new_i][new_j] = player_number
        return (aux[action], remaining_gas - self.cost(state, action))


    def is_goal_state(self, state):
        """ Check if a given state is goal

        For this particular agent, a goal is when the agent reaches any person
        """
        ag_pos, _, _, _ = self.__process_state(state)

        if ag_pos in self.people_position:
            return True
        return False


    def cost(self, state, action):
        """ Implements the step cost function

        Invalid actions have cost of 1
        STOP and REFILL has cost of 0 and
        Any other valid action has cost of 1
        """
        # Action is a invalid action, has cost of one gas unit
        if action not in self.actions(state):
            return 1
        # Action is valid, but it is a STOP or REFILL action, no cost
        if action in ['STOP', 'REFILL']:
            return 0
        return 1  # All other valid actions has cost 1


class RefillOrLeftAgent(util.Agent):
    """ A Simple test agent

    The RefillOrLeftAgent is an agent that respects the following police:
        - If it is inside a gas_station and its tank is not full, Refill
        - Else, just move left

    Our choice for a state to use in the search problem this agent will solve
    if a tuple with (agent_coordinates, remaining_fuel).

    .. notes::
        This agent does not care to check if LEFT is a valid action, meaning
        that except for the REFILL possibility, this agent always return
        LEFT (see LeftRefillProblem to understand how we processed the actions)

    .. seealso::
        GetClosestPersonOrRefillProblem
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @staticmethod
    def __find_pos(grid, player_number):
        # In case of multi_agent: agent01 (codes 1 and 8) and agent02 (2 and 9)
        if player_number == 2:
            current_player = [2, 9]
        else:
            current_player = [1, 8]

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] in current_player:
                    return (i, j)
        return None


    def get_action(self, perception):
        grid, rem_gas = perception
        if rem_gas == self.tank_capacity:
            return 'LEFT'
        else:
            player_pos = self.__find_pos(grid, self.player_number)
            i, j = player_pos
            if grid[i][j] == self.player_number + 7:
                return 'REFILL'
            return 'LEFT'


class DoNothingAgent(util.Agent):
    """ A Simple test agent

    The DoNothingAgent is an agent that respect the following police:
        - It always take the action STOP

    .. notes::
        Remember that STOP is always a valid action.
    """
    def __init__(self, player_number=2, **kwargs):
        super().__init__(player_number=player_number, **kwargs)
        self.initial_state = None


    def get_action(self, perception):
        return 'STOP'
