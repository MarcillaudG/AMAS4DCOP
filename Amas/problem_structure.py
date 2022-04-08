'''
A variable is an object with :
the possible values it can take
'''
import cexprtk
import itertools


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

    def __init__(self, name: str, all_variables_in_cons: [], values, objective: str, variables_domain = None):
        self.name = name
        self.objective = objective
        self.variables = [] + all_variables_in_cons
        self.variables_value = {}
        for variable in self.variables:
            self.variables_value[variable] = 0
        self.costs = {}
        self.costs_sorted = []
        self.dico_combination_to_cost = {}
        self.variables_domain = variables_domain
        self.best_cost = None
        self.worst_cost = None
        self.actual_cost = None

        # case of an expression
        if isinstance(values, str):
            self.type = "Function"
            self.expression = values
            self.init_combination()
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

            # create a list of sorted keys
            self.costs_sorted = sorted(self.costs.keys(), reverse=(self.objective == "max"))

            self.best_cost = self.costs_sorted[0]
            self.worst_cost = self.costs_sorted[-1]

    def init_combination(self):
        all_domains = []
        for variable in self.variables:
            all_domains.append(self.variables_domain[variable])

        iter_all_combi = itertools.product(*all_domains)

        for combination in iter_all_combi:
            for i in range(len(self.variables)):
                self.variables_value[self.variables[i]] = combination[i]
            self.compute_cost()

        # create a list of sorted keys
        self.costs_sorted = sorted(self.costs.keys(), reverse=(self.objective == "max"))

    def __str__(self):
        return "depending of variables : " + str(self.variables) + " "

    def compute_cost(self):
        if self.type == "Function":
            st = cexprtk.Symbol_Table(self.variables_value)
            e = cexprtk.Expression(self.expression, st)
            e.value()
            result = e.results()[0]

            # store the min and max
            if self.objective == "max":
                if self.best_cost is None or result > self.best_cost:
                    self.best_cost = result
                if self.worst_cost is None or result < self.worst_cost:
                    self.worst_cost = result
            else:
                if self.best_cost is None or result < self.best_cost:
                    self.best_cost = result
                if self.worst_cost is None or result > self.worst_cost:
                    self.worst_cost = result
            self.actual_cost = result


            # if the cost is unknown, adds it to the memory
            if result not in self.costs.keys():
                self.costs[result] = []
            actual_combination = tuple(self.variables_value.values())

            # if the combination is unknown, adds it to the known combination
            if actual_combination not in self.costs[result]:
                self.costs[result].append(actual_combination)
                self.dico_combination_to_cost[str(list(actual_combination))] = result

            return result
        else:
            combination = []
            for variable in self.variables:
                combination.append(self.variables_value[variable])
            combination_key = str(combination)
            result = self.dico_combination_to_cost[combination_key]
            self.actual_cost = result
            return result

    def find_value_best_cost_possible(self, var):
        ind_var = self.variables.index(var)
        i = 0
        over = False
        acceptable_values = []
        while i < len(self.costs_sorted) and self.is_better_cost(self.costs_sorted[i]):
            current_cost = self.costs_sorted[i]
            if isinstance(self.costs[current_cost], int):
                value = self.costs[current_cost]
                if value not in acceptable_values:
                    acceptable_values.append(value)
            else:
                for combination in self.costs[current_cost]:
                    if self.is_combination_possible(combination, ind_var):
                        value = combination[ind_var]
                        if value not in acceptable_values:
                            acceptable_values.append(value)
            i += 1
        return acceptable_values
        pass

    # Return if the new cost is better than the previous
    def is_better_cost(self, cost):
        if self.objective == "min":
            return self.actual_cost > cost
        else:
            return cost > self.actual_cost

    # return if a combination is possible with current variables value
    def is_combination_possible(self, combination, ind_var: int):
        i = 0
        res = True
        while i < len(combination):
            if i != ind_var and combination[i] != self.variables_value[self.variables[i]]:
                res = False
            i += 1
        return res
