"""
Author : Marcillaud Guilhem - SMAC
Year : 2022
"""
import random

from Amas.Problem_structure import Constraint, Variable


class Message:

    def __init__(self, id_sender: int, id_receiver: int, type: str):
        self.id_sender = id_sender
        self.id_receiver = id_receiver
        self.type = type


class MessageNotifyVariable(Message):

    def __init__(self, id_sender: int, id_receiver: int, vname : str, value):
        super().__init__(id_sender, id_receiver, "Notify_Variable")
        self.vname = vname
        self.value = value

class AMAS:

    def __init__(self, objective: str):
        self.objective = objective
        self.agents_constraints = []
        self.agents_variables = []
        self.domains = {}
        self.broker = None

    def init_solving(self):
        self.init_communication()
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

    # Create all constraint variables
    def distribute_constraints(self, all_constraints: {}):
        for cname in all_constraints.keys():
            c = Constraint(cname, all_constraints[cname][0], all_constraints[cname][1])
            self.agents_constraints.append(AgentConstraint(cname, c))
        print(str(self.agents_constraints))

    # Create all agents variables
    def distribute_variables(self, variables: {}):
        for variable in variables.keys():
            self.agents_variables.append(AgentVariable(variable, Variable(variable,
                                                                               self.domains[variables[variable]])))
        print(str(self.agents_variables))

    # Init the communication between constraints and variables
    def init_communication(self):
        self.broker = Broker()
        for agv in self.agents_variables:
            self.broker.init_communicating_agent(agv)

        for agc in self.agents_constraints:
            self.broker.init_communicating_agent(agc)
            variables_to_consider = agc.constraint.variables
            for variable in self.agents_variables:
                if variable.name in variables_to_consider:
                    variable.social_neighbours.append(agc.id_com)
                    variable.related_constraints.append(agc)
                    agc.social_neighbours.append(variable.id_com)




class Agent:
    def __init__(self, name: str):
        self.name = name
        self.mailbox = []
        self.broker = None
        self.id_com = -1
        self.social_neighbours = []

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

    def __init__(self, name: str, constraint: Constraint):
        super().__init__(name)
        self.constraint = constraint
        self.constraint_value = 0

    def read_mail(self):
        for message in self.mailbox:
            if message.type == "Notify_Variable":
                self.constraint.variables_value[message.vname] = message.value

    def perceive(self):
        self.read_mail()

    def decide(self):
        self.constraint_value = self.constraint.compute_cost()

    def act(self):
        print(self.__str__())
        print("Result of my constraint is : " + str(self.constraint_value))
        pass

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

    def random_value(self):
        tirage = random.randint(0, len(self.variable.values) - 1)
        self.value = self.variable.values[tirage]
        for constraint in self.related_constraints:
            self.communicate_value(constraint.id_com)

    def communicate_value(self, receiver: int):
        self.broker.send_message(MessageNotifyVariable(self.id_com, receiver, self.variable.name, self.value))
        pass

    def perceive(self):
        pass

    def decide(self):
        pass

    def act(self):
        print(self.__str__())
        print("My value is : " + str(self.value))
        pass

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
