"""
Author : Marcillaud Guilhem - SMAC
Year : 2022
"""
import cexprtk

from Amas.AMAS import AMAS
import yaml
"""
Global object, the required steps are :
1 : read the yaml file to extract the problem data and obtain the objective
2 : Create an AMAS object
3 : distribute the problem over agents in the AMAS
4 : Use the solve function
"""

dico_operateur = ["if", "else", "+", "-", "*", "/", "=", "=="]

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
                    self.constraints[cname] = (constraint_variables, all_values)
            if 'function' in data['constraints'][constraint_key].keys():
                function = data['constraints'][constraint_key]['function']
                function_split = function.split()
                first_ret = function_split[0]
                second_ret = function_split[-1]
                cond =  ""
                for i in range(1,len(function_split)-2):
                    tmp = function_split[i]
                    if tmp not in dico_operateur:
                        constraint_variables.append(tmp)
                    cond += tmp + " "
                    if "if" in tmp:
                        cond += "("
                cond += ") {return [" + first_ret + "]}"
                cond += " else {return [" + second_ret + "]}"
                self.constraints[cname] = (constraint_variables, cond)
        print(self.constraints)

    def distribute(self, nb_agents=0):

        pass

    def solve(self, max_cycle=100):
        pass

p = Problem("..\graph_coloring.yaml")

