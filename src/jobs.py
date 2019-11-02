import os.path


class Job:
    def __init__(self, nome, arvore, listaSegmentos):
        self.nome = nome
        self.arvore = arvore
        self.qtdSegmentos = len(listaSegmentos)
        self.listaSegmentos = listaSegmentos  # Lista de objetos da classe segmento
        self.segmentosAtivos = []  # Armazena o número dos segmentos ativos

    def mostrarArvore(self):
        print('\r\nArvore de segmentos do job ' + str(self.nome))
        print(self.arvore)

    def mostrarRequisitosDoJob(self):
        print('\r\nJob ' + str(self.nome))
        for seg in self.listaSegmentos:
            seg.mostrarRequisitos()

    def definirSegmentosAtivos(self, listaDeSegmentos):
        self.segmentosAtivos = listaDeSegmentos


class Segmento:
    def __init__(self, numero, memoria, tCPU, nomeE_S, qtdE_S, qtdArquivos, nomeDosArquivos, instantesDeAcesso, qtdDeReferenciasAOutrosSegms, segmsReferenciados, instantesDeReferencia, probabilidades):
        self.numero = numero
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

    def mostrarRequisitos(self):
        print('\r\nSegmento #' + str(self.numero))
        print('Memoria: ' + str(self.memoria))
        print('Tempo de CPU: ' + str(self.tCPU))
        if(self.nomeE_S):
            print('Nome do dispositivos de E/S acessado: ' + str(self.nomeE_S))
            print('Quantidades de acesso ao dispositivo de E/S: ' + str(self.qtdE_S))
        print('Quantidade de arquivos a serem acessados: ' + str(self.qtdArquivos))
        if(self.qtdArquivos > 0):
            for i in range(self.qtdArquivos):
                print('Arquivo ' + self.nomeDosArquivos[i] + ' acessado no instante ' + str(self.instantesDeAcesso[i]))
        print('Quantidade de referências a outros segmentos: ' + str(self.qtdDeReferenciasAOutrosSegms))
        if(self.qtdDeReferenciasAOutrosSegms > 0):
            for i in range(self.qtdDeReferenciasAOutrosSegms):
                print('Referencia-se o segmento ' + str(self.segmsReferenciados[i]) + ' no instante ' + str(self.instantesDeReferencia[i]) + ' com probabilidade ' + str(100 * self.probabilidades[i]) + '%')

def lerJobDoArquivo(nomeArquivo: str):
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

    # Requisitos serão expressos como atributos da classe segmento, cada elemento será da forma:
    # [memoria, tCPU, nomeE_S, qtdE_S, qtdArquivos, [nomeDosArquivos], [instantesDeAcesso], qtdDeReferenciasAOutrosSegms, [segmsReferenciados], [instanteDeReferencia],[probabilidade]]
    listaDeSegmentos = []
    for seg in range(qtdSegmentos):
        elementosDaLinha = linhas[seg + 2].split(',')
        memoria = int(elementosDaLinha[0])
        tCPU = int(elementosDaLinha[1])
        nomeE_S = elementosDaLinha[2]
        qtdE_S = elementosDaLinha[3]
        qtdArquivos = int(elementosDaLinha[4])
        index = 5
        nomeDosArquivos = []
        for i in range(qtdArquivos):
            nomeDosArquivos.append(elementosDaLinha[index])
            index += 1
        instantesDeAcesso = []
        for i in range(qtdArquivos):
            instantesDeAcesso.append(int(elementosDaLinha[index]))
            index += 1
        qtdDeReferenciasAOutrosSegms = int(elementosDaLinha[index])
        index += 1
        segmsReferenciados = []
        instantesDeReferencia = []
        probabilidades = []
        for i in range(qtdDeReferenciasAOutrosSegms):
            segmsReferenciados.append(int(elementosDaLinha[index]))
            index += 1
        for i in range(qtdDeReferenciasAOutrosSegms):
            instantesDeReferencia.append(int(elementosDaLinha[index]))
            index += 1
        for i in range(qtdDeReferenciasAOutrosSegms):
            probabilidades.append(float(elementosDaLinha[index]))
            index += 1
        novoSegmento = Segmento(numero=seg, memoria=memoria, tCPU=tCPU, nomeE_S=nomeE_S, qtdE_S=qtdE_S, qtdArquivos=qtdArquivos, nomeDosArquivos=nomeDosArquivos,
                                instantesDeAcesso=instantesDeAcesso, qtdDeReferenciasAOutrosSegms=qtdDeReferenciasAOutrosSegms, segmsReferenciados=segmsReferenciados,
                                instantesDeReferencia=instantesDeReferencia, probabilidades=probabilidades)
        listaDeSegmentos.append(novoSegmento)
    # print(requisitos)
    novoJob = Job(nome=nomeArquivo.split('.')[0], arvore=arvoreSegmentos, listaSegmentos=listaDeSegmentos)
    return novoJob

def montarTabelaDeJobs(listaDeNomes):
    # A tabela será implementada através de dicts. A chave é o nome do job e o conteúdo representa os recursos
    # a serem alocados para cada segmento
    tabelaDeJobs = []
    for nomeDoJob in listaDeNomes:
        tabelaDeJobs.append(lerJobDoArquivo(nomeDoJob))

    return tabelaDeJobs


# listaDeNomes = ['A.txt']
# tabelaDeJobs = montarTabelaDeJobs(listaDeNomes=listaDeNomes)
# for job in tabelaDeJobs:
#     job.mostrarRequisitosDoJob()
#     job.mostrarArvore()
