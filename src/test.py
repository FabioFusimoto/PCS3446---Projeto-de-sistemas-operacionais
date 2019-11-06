d = {}
d['A', 'E0'] = [333, 666]
d['A', 'S1'] = [1075]
d['B', 'E0'] = [333, 666]

instantesA = []
chaves = [chave for chave in d.keys() if chave[0] == 'A']
for chave in chaves:
    for instante in d[chave]:
        instantesA.append(instante)
print(instantesA)
