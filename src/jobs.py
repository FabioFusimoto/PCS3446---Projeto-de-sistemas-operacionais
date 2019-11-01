import os.path


class Job:
    def __init__(self, arvore, listaSegmentos):
        self.arvore = arvore
        self.qtdSegmentos = len(listaSegmentos)
        self.listaSegmentos = listaSegmentos


class Segmento:
    def __init__(self, memoria, tCPU, nomeE_S, qtdE_S, qtdArquivos, *nomeDosArquivos, *instantesDeAcesso, qtdDeReferenciasAOutrosSegms, *segmsReferenciados, *instantesDeReferencia, *probabilidades):
        self.memoria = memoria
        self.tCPU = tCPU
        self.nomeE_S = nomeE_S
        self.qtdE_S = qtdE_S
        self.qtdArquivos = qtdArquivos
        self.nomeDosArquivos = nomeDosArquivos
        self.instantesDeAcesso = instantesDeAcesso
        self.qtdDeReferenciasAOutrosSegms = qtdDeReferenciasAOutrosSegms
        self.segmsReferenciados = segmsReferenciados
        self.instantesDeReferencia = instantesDeReferencia
        self.probabilidades = probabilidades

    def mostrarRequisitosDoSegmento(self):
        pass


def lerJobsDoArquivo(nomeArquivo: str):
    # retorna uma entrada para colocar na tabela de jobs
    f = open(os.path.split(os.path.dirname(__file__))[0] + '/txt/jobs/' + str(nomeArquivo), 'r')
    linhas = f.readlines()
    f.close()
    # for element in f:
    #     print(element)

    # Gerando a árvore de segmentos
    # arvore[número_do_segmento] = [pai, [lista de filhos]]
    arvoreSegmentos = {}
    vertices = linhas[0].split('\n')[0].split(',')  # tem o split('\n') para eliminar o caractere \n que tem em cada linha
    for v in vertices:
        pai = int(v.split('-')[0])
        filhos = list(map(int, v.split('-')[1].split(' ')))  # converte todos os elementos da lista em int
        if(pai not in arvoreSegmentos.keys()):
            arvoreSegmentos[pai] = [None, filhos]  # isso vai acontecer somente para o nó 0
        else:
            for f in filhos:
                arvoreSegmentos[pai][1].append(f)
        # depois de tratar os pais, é necessário inserir os filhos no dicionário
        for f in filhos:
            if (f not in arvoreSegmentos.keys()):
                arvoreSegmentos[f] = [pai, []]

    # print(arvoreSegmentos)

    # Para cada segmento, verificar quais os requisitos
    qtdSegmentos = int(linhas[1])
    # print('Quantidade de segmentos = ' + str(qtdSegmentos))

    # Requisitos serão expressos como listas de dicionários, cada elemento será da forma:
    # [Memoria, tCPU, nomeE_S, qtdE_S, qtdArquivos, [nomeDosArquivos], [instantesDeAcesso], qtdDeReferenciasAOutrosSegms, [segmsReferenciados], [instanteDeReferencia],[probabilidade]]
    requisitos = []
    for seg in range(qtdSegmentos):
        dictSeg = {}
        elementosDaLinha = linhas[seg + 2].split(',')
        dictSeg['Memoria'] = int(elementosDaLinha[0])
        dictSeg['tCPU'] = int(elementosDaLinha[1])
        dictSeg['nomeE_S'] = elementosDaLinha[2]
        dictSeg['qtdE_S'] = elementosDaLinha[3]
        dictSeg['qtdArquivos'] = int(elementosDaLinha[4])
        index = 5
        nomeDosArquivos = []
        if(dictSeg['qtdArquivos'] > 0):
            for i in range(dictSeg['qtdArquivos']):
                nomeDosArquivos.append(elementosDaLinha[index])
                index += 1
        dictSeg['nomeDosArquivos'] = nomeDosArquivos
        instantesDeAcesso = []
        if(dictSeg['qtdArquivos'] > 0):
            for i in range(dictSeg['qtdArquivos']):
                instantesDeAcesso.append(int(elementosDaLinha[index]))
                index += 1
        dictSeg['instantesDeAcesso'] = instantesDeAcesso
        dictSeg['qtdReferenciasAOutrosSegms'] = int(elementosDaLinha[index])
        index += 1
        segmsReferenciados = []
        instantesDeReferencia = []
        probabilidades = []
        if(dictSeg['qtdReferenciasAOutrosSegms'] > 0):
            for i in range(dictSeg['qtdReferenciasAOutrosSegms']):
                segmsReferenciados.append(int(elementosDaLinha[index]))
                index += 1
            for i in range(dictSeg['qtdReferenciasAOutrosSegms']):
                instantesDeReferencia.append(int(elementosDaLinha[index]))
                index += 1
            for i in range(dictSeg['qtdReferenciasAOutrosSegms']):
                probabilidades.append(float(elementosDaLinha[index]))
                index += 1
        dictSeg['segmsReferenciados'] = segmsReferenciados
        dictSeg['instantesDeReferencia'] = instantesDeReferencia
        dictSeg['probabilidades'] = probabilidades
        requisitos.append(dictSeg)

    # print(requisitos)
    return arvoreSegmentos, requisitos


def montarTabelaDeJobs(*listaDeJobs):
    # A tabela será implementada através de dicts. A chave é o nome do job e o conteúdo representa os recursos
    # a serem alocados para cada segmento
    tabelaDeJobs = []
    for nome in listaDeJobs:
        arvore, requisitos = lerJobsDoArquivo(nome)
        tabelaDeJobs.append([nome, arvore, requisitos])

    return tabelaDeJobs


# listaDeJobs = ['A.txt']
# tabelaDeJobs = montarTabelaDeJobs(*listaDeJobs)
# print(tabelaDeJobs)
