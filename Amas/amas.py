"""
Author : Marcillaud Guilhem - SMAC
Year : 2022
"""
import random

from Amas.problem_structure import Constraint, Variable


class Message:

    def __init__(self, id_sender: int, id_receiver: int, type: str):
        self.id_sender = id_sender
        self.id_receiver = id_receiver
        self.type = type


class MessageNotifyVariable(Message):

    def __init__(self, id_sender: int, id_receiver: int, vname: str, value):
        super().__init__(id_sender, id_receiver, "Notify_Variable")
        self.vname = vname
        self.value = value


class MessageRequestVariable(Message):

    def __init__(self, id_sender: int, id_receiver: int, values: [], criticality: float):
        super().__init__(id_sender, id_receiver, "Request")
        self.values = values
        self.requester_criticality = criticality


class AMAS:

    def __init__(self, objective: str):
        self.objective = objective
        self.agents_constraints = []
        self.agents_variables = []
        self.domains = {}
        self.broker = None

    def init_solving(self):
        self.__init_communication__()
        self.__init_criticalities__()
        for agv in self.agents_variables:
            agv.random_value()

    """
    First the agents variables then the agents constraints
    """

    def cycle(self):
        for agent_variable in self.agents_variables:
            agent_variable.perceive()
            agent_variable.decide()
            agent_variable.act()

        for agent_constraint in self.agents_constraints:
            agent_constraint.perceive()
            agent_constraint.decide()
            agent_constraint.act()
        input()

    # Create all constraint variables
    def distribute_constraints(self, all_constraints: {}):
        for cname in all_constraints.keys():
            if len(all_constraints[cname]) == 2 :
                c = Constraint(cname, all_constraints[cname][0], all_constraints[cname][1], self.objective)
            if len(all_constraints[cname]) == 3 :
                c = Constraint(cname, all_constraints[cname][0], all_constraints[cname][1], self.objective,
                               all_constraints[cname][2])

            self.agents_constraints.append(AgentConstraint(cname, c, self.objective))
        print(str(self.agents_constraints))

    # Create all agents variables
    def distribute_variables(self, variables: {}):
        for variable in variables.keys():
            self.agents_variables.append(AgentVariable(variable, Variable(variable,
                                                                          self.domains[variables[variable]])))
        print(str(self.agents_variables))

    # Init the communication between constraints and variables
    def __init_communication__(self):
        print("Initialisation of communication")
        self.broker = Broker()
        for agv in self.agents_variables:
            self.broker.init_communicating_agent(agv)

        for agc in self.agents_constraints:
            self.broker.init_communicating_agent(agc)
            variables_to_consider = agc.constraint.variables
            for variable in self.agents_variables:
                if variable.name in variables_to_consider:
                    variable.social_neighbours[agc.name] = agc.id_com
                    variable.related_constraints.append(agc)
                    agc.social_neighbours[variable.name] = variable.id_com
        print("End of initialisation of communication")

    def __init_criticalities__(self):
        print("Initialisation of criticalities")
        max_etendue = 0
        # TODO Can be improved
        print("Collecting value range of constraints")
        for agc in self.agents_constraints:
            min_agc = agc.constraint.worst_cost
            max_agc = agc.constraint.best_cost
            etendue = abs(max_agc - min_agc)
            max_etendue = max(max_etendue, etendue)
        coeff = 100 / max_etendue
        print("The max value range is " + str(max_etendue) + " and the coeff value is " + str(coeff))
        print("Computation of weight for criticality computation")
        for agc in self.agents_constraints:
            min_agc = agc.constraint.worst_cost
            max_agc = agc.constraint.best_cost
            etendue = abs(max_agc - min_agc)
            agc.weight_constraint = etendue * coeff
            print(str(agc) + " " + str(agc.weight_constraint))
        print("End of initialisation of criticalities")
        input()


class Agent:
    def __init__(self, name: str):
        self.name = name
        self.mailbox = []
        self.broker = None
        self.id_com = -1
        self.social_neighbours = {}

    def perceive(self):
        pass

    def decide(self):
        pass

    def act(self):
        pass

    def communicate(self, receiver: str):
        pass

    def init_communication(self, broker):
        self.broker = broker

    def read_mail(self):
        pass


class AgentConstraint(Agent):

    def __init__(self, name: str, constraint: Constraint, objective: str):
        super().__init__(name)
        self.constraint = constraint
        self.objective = objective
        self.constraint_value = 0
        self.criticality = 0.0
        self.anticipated_criticality = 0.0
        self.weight_constraint = 0.0
        self.action = None
        self.sending_box = []

        # used to store criticality
        # Keys = variable name
        # value is a couple with the mutation criticality in first and assistance in second
        self.variables = {}

        # Init agent variables representation
        for variable in self.constraint.variables:
            self.variables[variable] = (0.0, 0.0)

    def read_mail(self):
        for message in self.mailbox:
            if message.type == "Notify_Variable":
                self.constraint.variables_value[message.vname] = message.value

    def perceive(self):
        self.read_mail()

    def decide(self):
        self.constraint_value = self.constraint.compute_cost()
        old_criticality = self.criticality

        self.compute_criticality()

        if self.criticality == 0:
            self.action = "NOTHING"
        if self.criticality > 0 and old_criticality != self.criticality:
            self.action = "REQUEST"
            # Choose interesting values and agent

            # First look for variable that may want to listen to me
            # and sort it by their criticality
            less_critical_variables = self.insertion_var_par_dichotomie()

            # Second look at what values could be interesting
            values_possible = []
            chosen_var = None
            i = 0
            over = False
            var = None
            while i < len(less_critical_variables) and not over:
                var = less_critical_variables[i][1]
                values_possible = self.constraint.find_value_best_cost_possible(var)
                if values_possible != []:
                    over = True
                i += 1

            # Creation of messages
            self.sending_box.append(MessageRequestVariable(self.id_com, self.social_neighbours[var],
                                                           values_possible, self.criticality))

    def act(self):
        print(self.__str__())
        print("Result of my constraint is : " + str(self.constraint_value))
        for message in self.sending_box:
            self.broker.send_message(message)
        pass

    def insertion_var_par_dichotomie(self):
        nb_var = 0
        less_critical_variables = []
        for variable in self.variables.keys():
            crit_var = self.variables[variable][1]
            if crit_var < self.criticality:

                # dichotomy
                milieu = 0
                if less_critical_variables != []:
                    if less_critical_variables[0][0] < crit_var:
                        inf, sup = 0, nb_var
                        milieu = (inf + sup) // 2
                        while inf + 1 < sup:
                            m = (inf + sup) // 2
                            if less_critical_variables[m][0] <= crit_var:
                                inf = m
                            else:
                                sup = m
                less_critical_variables.insert(milieu, (crit_var, variable))
                nb_var += 1
        return less_critical_variables

    # Return if the new cost is better than the previous
    def is_better_cost(self, actual, cost):
        if self.objective == "min":
            return actual > cost
        else:
            return cost > actual
        pass

    def compute_criticality(self):
        if self.constraint.best_cost - self.constraint.worst_cost == 0:
            self.criticality = 0.0
        else:
            self.criticality = abs(self.constraint_value - self.constraint.best_cost) * self.weight_constraint

    def __str__(self):
        return "Agent Constraint with constraint " + str(self.constraint)

    def __repr__(self):
        return "Agent Constraint with constraint " + str(self.constraint)


class AgentVariable(Agent):
    def __init__(self, name: str, variable: Variable):
        super().__init__(name)
        self.variable = variable
        tirage = random.randint(0, len(variable.values) - 1)
        self.value = variable.values[tirage]
        self.related_constraints = []
        self.waiting_request = []
        self.value_to_take = None

        self.assist_criticality = 0.0
        self.mutate_criticality = 0.0

        # list with couples of variables that are blocked because of constraints
        self.impossible_variables = []

    def random_value(self):
        tirage = random.randint(0, len(self.variable.values) - 1)
        self.value = self.variable.values[tirage]
        for constraint in self.related_constraints:
            self.communicate_value(self.social_neighbours[constraint.constraint.name])

    def communicate_value(self, receiver: int):
        self.broker.send_message(MessageNotifyVariable(self.id_com, receiver, self.variable.name, self.value))
        pass

    def perceive(self):
        self.read_mail()
        self.value_to_take = None
        pass

    def decide(self):
        # If no request, do nothing
        if len(self.waiting_request) == 0:
            self.value_to_take = self.value
        else:
            self.value_to_take, nb_waiting_to_remove = self.choose_best_value()

            # Remove all waiting that are satisfied
            # Warning Only Works with proposition 1
            for i in range(nb_waiting_to_remove - 1):
                self.waiting_request = self.waiting_request[1:]
            pass

    def act(self):
        if self.value != self.value_to_take and self.value_to_take is not None:
            self.value = self.value_to_take
            for constraint in self.related_constraints:
                self.communicate_value(self.social_neighbours[constraint.name])
        print(self.__str__())
        print("My value is : " + str(self.value))
        pass

    # Add to the waiting  request all messages from the cycle
    def read_mail(self):
        for message in self.mailbox:
            # If it is a request message then it is added to the waiting request, ordered by criticality
            if isinstance(message, MessageRequestVariable):
                if len(self.waiting_request) == 0:
                    self.waiting_request.append(message)
                else:
                    crit_mess = message.requester_criticality
                    inf = 0
                    sup = len(self.waiting_request) - 1
                    m = (inf + sup) // 2
                    while inf + 1 < sup:
                        m = (inf + sup) // 2
                        if self.waiting_request[m].requester_criticality <= crit_mess:
                            inf = m
                        else:
                            sup = m
                    self.waiting_request.insert(m, message)
        pass

    # Proposition 1, we choose the value that helps the most critical
    def choose_best_value(self):
        # Take the most critical request
        most_critical = self.waiting_request[0]
        i = 0
        values_requested = most_critical.values
        over = False
        best_value = None
        nb_best = 0
        while i < len(values_requested) and not over:
            value = values_requested[i]
            nb_constraint_satisfied = 1
            accepted = True
            j = 1
            while j < len(self.waiting_request[1:]) and accepted:
                if value not in self.waiting_request[j].values:
                    accepted = False
                else:
                    nb_constraint_satisfied += 1
                j += 1
            if nb_constraint_satisfied > nb_best:
                best_value = value
                nb_best = nb_constraint_satisfied
            i += 1
        return best_value, nb_best

    def __str__(self):
        return "Agent Variable with variable " + str(self.variable)

    def __repr__(self):
        return "Agent Variable with variable " + str(self.variable)


'''
Class used to enable communication between agents
'''


class Broker:
    def __init__(self):
        self.agents = {}
        self.id_com = 0
        self.count_message = 0

    def init_communicating_agent(self, agent: Agent):
        agent.broker = self
        agent.id_com = self.id_com
        self.agents[self.id_com] = agent
        self.id_com += 1

    def send_message(self, message: Message):
        self.agents[message.id_receiver].mailbox.append(message)
        self.count_message += 1
