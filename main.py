import cexprtk
import itertools
'''
stream = open("graph_coloring.yaml")
data = yaml.load(stream)

print(data.keys())
print(data)'''


costs = {7: 1, 9 : 3, 1: 4, -6 : 18}

costs = dict(sorted(costs.items(), reverse=True))
over = False
for elem in costs.keys() and not over:
    if elem > 1:
        over = True
    print(elem)