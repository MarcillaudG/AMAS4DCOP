'''
A variable is an object with :
the possible values it can take
'''
import cexprtk


class Variable:

    def __init__(self, name: str, values: []):
        self.name = name
        self.values = values

    def __str__(self):
        return self.name + str(self.values)

'''
Combination is composed of variables and the cost associated to their value
Used to store value
'''


class Combination:

    def __init__(self, id: int, variables: [], variables_cost: [], cost: float):
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

    def __init__(self, name: str, all_variables_in_cons: [], values):
        self.name = name
        self.variables = [] + all_variables_in_cons
        self.variables_value = {}
        for variable in self.variables:
            self.variables_value[variable] = 0
        self.costs = {}
        self.dico_combination_to_cost = {}
        self.max_cost = None
        self.min_cost = None


        # case of an expression
        if isinstance(values, str):
            self.type = "Function"
            self.expression = values
        else:
            self.type = "Combination"
            if isinstance(values, dict):
                for value_cost in values.keys():
                    self.costs[value_cost] = []
                    split_costs = values[value_cost].split("|")
                    for elem in split_costs:
                        var_comb = []
                        for value_var in elem.split():
                            var_comb.append(int(value_var))
                        self.costs[value_cost].append(var_comb)
                        self.dico_combination_to_cost[var_comb] = value_cost
            else:
                for cost, var_value in values:
                    if cost not in self.costs.keys():
                        self.costs[cost] = []
                    self.costs[cost] = var_value
                    key_var_value = str([var_value])
                    self.dico_combination_to_cost[key_var_value] = cost
            self.max_cost = max(list(self.costs.keys()))
            self.min_cost = min(list(self.costs.keys()))


    def __str__(self):
        return "depending of variables : " + str(self.variables) + " "

    def compute_cost(self):
        if self.type == "Function":
            st = cexprtk.Symbol_Table(self.variables_value)
            e = cexprtk.Expression(self.expression, st)
            e.value()
            result = e.results()[0]
            if self.max_cost is None or result > self.max_cost:
                self.max_cost = result
            if self.min_cost is None or result < self.min_cost:
                self.min_cost = result
            return result
        else:
            combination = []
            for variable in self.variables:
                combination.append(self.variables_value[variable])
            combination_key = str(combination)
            result = self.dico_combination_to_cost[combination_key]
            return result