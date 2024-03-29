import texttable


class RAM:
    def __init__(self, tamanho):
        # Tamanho expresso em bytes
        self.tamanho = tamanho

        # A segmentTable terá a forma ST[str(job) + str(segmento)] = [endInicial, tamanhoDoSegmento]
        self.segmentTable = {}

        # A file table terá a forma FT[nomeDoArquivo] = [dono, [jobsDependentes]]
        # O dono pode ser 'Public' ou ter o nome de um job. Se for 'Public' qualquer job pode acessar contanto que esteja na memória
        # Quando o dono for removido da memória, o arquivo também o será. Mas se o dono for 'Public' mantém-se o arquivo na memória até que todos os dependentes sejam encerrados
        self.fileTable = {}

        # Os espaços ocupados serão representados da forma [inicio, fim] --> [[0,199], [250,449], [450, 999]] --> segmentos de tamanho 200, 250 e 550
        # As duplas estão expressas sempre em ordem crescente
        self.espacosOcupados = []

        # Fila de elementos da classe Job
        self.fila = []

    def verificarDisponibilidadeDeMemoria(self, qtdMem):  # Retorna True, endereço se houver um espaço disponível ou False, None se não houver
        # Se a memória estiver vazia, aloca-se na posição 0
        if (len(self.espacosOcupados) == 0):
            # print('Lista vazia, insere-se o job no início')
            return True, 0

        # Depois vejo se há espaço livre entre a posição 0 e o início do primeiro espaço ocupado
        if(self.espacosOcupados[0][0] >= qtdMem):
            # print('Lista não vazia, mas insere-se o job no início')
            return True, 0

        # Depois vejo se há espaço disponível entre 2 jobs
        if(len(self.espacosOcupados) >= 2):
            for i in range(len(self.espacosOcupados) - 1):
                if(self.espacosOcupados[i + 1][0] - self.espacosOcupados[i][1]) > qtdMem:
                    # print('Insere-se o  job entre as posições ' + str(self.espacosOcupados[i][1]) + ' e ' + str(self.espacosOcupados[i + 1][0]))
                    return True, (self.espacosOcupados[i][1] + 1)

        # Por fim vejo se há espaço disponível após o job que ocupa a última posição da ordem
        if(self.tamanho - 1 - self.espacosOcupados[len(self.espacosOcupados) - 1][1]) >= qtdMem:
            # print('Insere-se o job ao final da memória, a partir da posição ' + str(self.espacosOcupados[len(self.espacosOcupados) - 1][1] + 1))
            return True, (self.espacosOcupados[len(self.espacosOcupados) - 1][1] + 1)

        # Se todos as condições anteriores falharem, significa que não há espaço para o job que se quer alocar
        return False, None

    def alocarJobDaFila(self):
        # O elemento de maior prioridade encontra-se na última posição da fila, posição (len(self.fila) - 1)

        # Retorna-se True, nomeDoJob caso o job seja alocado na memória
        # Retorna-se False, None caso não haja nenhum job para ser alocado
        if len(self.fila) == 0:
            return False, None

        # Calcula-se primeiro quanta memória será necessária para alocar todos os segmentos ativos do job
        memoriaNecessaria = 0
        for segm in self.fila[len(self.fila) - 1].segmentosAtivos:
            memoriaNecessaria += self.fila[len(self.fila) - 1].listaSegmentos[segm].memoria
        haMemoriaDisponivel, posicaoParaAlocar = self.verificarDisponibilidadeDeMemoria(qtdMem=memoriaNecessaria)
        if(haMemoriaDisponivel):
            nomeDoJob = self.fila[len(self.fila) - 1].nome
            # Atualizando a tabela de segmentos e os espaços ocupados
            for segm in self.fila[len(self.fila) - 1].segmentosAtivos:
                tamanhoDoSegmento = self.fila[len(self.fila) - 1].listaSegmentos[segm].memoria
                self.segmentTable[str(nomeDoJob) + str(segm)] = [posicaoParaAlocar, tamanhoDoSegmento]
                self.espacosOcupados.append([posicaoParaAlocar, posicaoParaAlocar + tamanhoDoSegmento - 1])
                posicaoParaAlocar += tamanhoDoSegmento

            # Reorganizando a lista de espaços ocupados para sempre permanecer em ordem crescente
            self.espacosOcupados.sort(key=lambda x: x[0])

            # Ao término da execução, remove-se o job da fila
            nomeDoJob = self.fila.pop().nome
            return True, nomeDoJob
        else:
            return False, None

    def alocarNovoJob(self, job):
        self.fila.insert(0, job)

    def liberarJob(self, nomeDoJob):
        # Primeiro consulta-se a segmentTable para ver quais posições são pertinentes ao job que se quer remover
        chavesADeletar = []
        for key in self.segmentTable.keys():
            if nomeDoJob in key:
                # Liberando o espaço
                for i in range(len(self.espacosOcupados)):
                    if(self.espacosOcupados[i][0] == self.segmentTable[key][0]):
                        del self.espacosOcupados[i]
                        break

                # Para atualizar a tabela de segmentos
                chavesADeletar.append(key)  # Não posso deletar dentro do laço porque estou iterando sobre as chaves

        # Verificando quais arquivos devem ser removidos da memória
        nomesDeArquivosParaDeletar = []
        for nomeArquivo in self.fileTable.keys():
            if(nomeDoJob in self.fileTable[nomeArquivo][1]):
                # print('O job ' + nomeDoJob + ' depende do arquivo ' + nomeArquivo)
                if len(self.fileTable[nomeArquivo][1]) == 1:
                    nomesDeArquivosParaDeletar.append(nomeArquivo)
                else:
                    # Se mais de um job depender do arquivo, não se pode deletá-lo, apenas remover sua dependência da lista
                    indiceParaRemover = self.fileTable[nomeArquivo][1].index(nomeDoJob)
                    del(self.fileTable[nomeArquivo][1][indiceParaRemover])

        # Deletando os arquivos
        for nome in nomesDeArquivosParaDeletar:
            del self.fileTable[nome]

        # Deletando as entradas pertinentes da tabela de segmentos
        for key in chavesADeletar:
            del self.segmentTable[key]

    def verificarPresencaDeSegmento(self, nomeDoJob, numeroDoSegmento):
        if(str(nomeDoJob) + str(numeroDoSegmento)) in self.segmentTable.keys():
            return True
        else:
            return False

    def carregarArquivoDoDisco(self, nomeDoArquivo, jobSolicitante, disco):
        # O arg disco é um objeto da classe disco
        # Carrega-se o arquivo do disco para a memória

        # Arquivo não presente ainda em memória
        if nomeDoArquivo not in self.fileTable.keys():
            if('Public' in disco.arquivos[nomeDoArquivo][1]):
                dono = 'Public'
            else:
                dono = jobSolicitante
            self.fileTable[nomeDoArquivo] = [dono, [jobSolicitante]]
        else:
            # Arquivo presente na memória e no caso que jobs acesse o arquivo simultaneamente
            self.fileTable[nomeDoArquivo][1].append(jobSolicitante)

    def mostrarSegmentTable(self):
        t = texttable.Texttable()
        print('\r\nSegment table')
        t.add_row(['Job + Segmento', 'Endereço inicial de alocação', 'Tamanho'])
        for key in self.segmentTable.keys():
            t.add_row([key, self.segmentTable[key][0], self.segmentTable[key][1]])
        print(t.draw())

    def mostrarFileTable(self):
        t = texttable.Texttable()
        print('\r\nFile table')
        t.add_row(['Nome do arquivo', 'Dono do arquivo', 'Jobs dependentes'])
        for key in self.fileTable.keys():
            t.add_row([key, self.fileTable[key][0], self.fileTable[key][1]])
        print(t.draw())

    def mostrarEspacosOcupados(self):
        t = texttable.Texttable()
        print('\r\nEspaços ocupados')
        t.add_row(['Endereço inicial', 'Endereço final'])
        for dupla in self.espacosOcupados:
            t.add_row([dupla[0], dupla[1]])
        print(t.draw())
