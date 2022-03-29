import cexprtk
'''
stream = open("graph_coloring.yaml")
data = yaml.load(stream)

print(data.keys())
print(data)'''




l = [(6, "A"), (7, "B"), (3,"C"), (4, "E")]
l.sort()
print(l)


def insertion_par_dichotomie(tab, elem):
    valeur = elem[0]
    milieu = 0
    if tab != []:
        if tab[0][0] < valeur:
            inf, sup = 0, len(tab)
            milieu = (inf + sup) // 2
            while inf + 1 < sup:
                m = (inf + sup) // 2
                if tab[m][0] <= valeur:
                    inf = m
                else:
                    sup = m
    tab.insert(milieu, elem)

insertion_par_dichotomie(l, (5, "D"))
print(l)