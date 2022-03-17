import yaml


stream = open("graph_coloring.yaml")
data = yaml.load(stream)

print(data.keys())
print(data)