"""
Author : Marcillaud Guilhem - SMAC
Year : 2022
"""


'''
A variable is an object with :
the possible values it can take
'''


class Variable:

    def __init__(self, name: str, values: []):
        self.name = name
        self.values = values

'''
Combination is composed of variables and the cost associated to their value
Used to store value
'''


class Combination:

    def __init__(self, id: int, variables: [], cost: float):
        self.id = id
        self.variables = variables
        self.cost = cost

    def __str__(self):
        return "Combination : " + str(self.id) + " " + str(self.variables)


'''
A constraint is an object with :
The set of variables involved
The cost induced by each combination of variables
'''


class Constraint:

    def __init__(self, name: str, all_variables_in_cons: []):
        self.name = name
        self.variables = {}
        self.costs = {}

        for var in all_variables_in_cons:
            self.variables[var.name] = var

    def compute_cost(self):
        pass



class AMAS:

    def __init__(self, objective: str):
        self.objective = objective
        self.agents_constraints = {}
        self.agents_variables = {}

    """
    First the agents variables then the agents constraints
    """
    def cycle(self):
        for agent_variable in self.agents_variables.values():
            agent_variable.perceive()
            agent_variable.decide()
            agent_variable.act()

        for agent_constraint in self.agents_constraints.values():
            agent_constraint.perceive()
            agent_constraint.decide()
            agent_constraint.act()

    def create_constraint(self, cname: str, all_variables_in_cons: []):
        c = Constraint(cname, all_variables_in_cons)
        self.agents_constraints[cname] = AgentConstraint(cname, c)


class Agent:
    def __init__(self, name: str):
        self.name = name
        self.mailbox = {}

    def perceive(self):
        pass

    def decide(self):
        pass

    def act(self):
        pass

    def communicate(self, receiver: str, type_receiver: str):
        pass

class AgentConstraint(Agent):

    def __init__(self, name: str, constraint: Constraint):
        super().__init__(name)
        self.constraint = constraint

class AgentVariable(Agent):
    def __init__(self, name: str, variable: Variable):
        super().__init__(name)
        self.variable = variable


