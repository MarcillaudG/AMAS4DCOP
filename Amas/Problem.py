"""
Author : Marcillaud Guilhem - SMAC
Year : 2022
"""
from Amas.AMAS import AMAS
import yaml
"""
Global object, the required steps are :
1 : read the yaml file to extract the problem data and obtain the objective
2 : Create an AMAS object
3 : distribute the problem over agents in the AMAS
4 : Use the solve function
"""


class Problem:

    def __init__(self, filename: str):
        self.objective = "min"
        self.constraints = {}
        self.variables = {}
        self.domains = {}
        self.extract_data(filename)
        self.amas = AMAS(self.objective)

    def extract_data(self, filename: str):
        stream = open(filename)
        data = yaml.load(stream)

        self.name = data['name']
        self.objective = data['objective']

        # domains extraction
        for domain_key in data['domains'].keys():
            dname = domain_key
            values = data['domains'][domain_key]['values']
            self.domains[dname] = values
        print(str(self.domains))

        # variables extraction
        for variable_key in data['variables'].keys():
            vname = variable_key
            vdomain = data['variables'][variable_key]['domain']
            self.variables[vname] = vdomain
        print(str(self.variables))

        # constraints extraction
        for constraint_key in data['constraints'].keys():
            cname = constraint_key
            constraint_variables = []
            all_values = []
            if 'variables' in data['constraints'][constraint_key].keys():
                dico_variables_cons = data['constraints'][constraint_key]['variables']
                if isinstance(dico_variables_cons,str):
                    constraint_variables.append(dico_variables_cons)
                else:
                    all_var = []
                    for variable in dico_variables_cons:
                        all_var.append(variable)
                    constraint_variables.append(all_var)
            if 'values' in data['constraints'][constraint_key].keys():
                for value_cost in data['constraints'][constraint_key]['values'].keys():
                    all_values.append((value_cost, data['constraints'][constraint_key]['values'][value_cost]))
            if 'function' in data['constraints'][constraint_key].keys():
                raise Exception('Function not supported yet','eggs')
            self.constraints[cname] = (constraint_variables, all_values)
        print(self.constraints)

    def distribute(self, nb_agents=0):
        pass

    def solve(self, max_cycle=100):
        pass

p = Problem("..\graph_coloring.yaml")

