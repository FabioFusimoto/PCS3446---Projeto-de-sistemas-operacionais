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

    def verificarDisponibilidadeDeMemoria(self, qtdMem):  # Retorna True, endereço sehouber um espaço disponível ou False, None se não houver
        # Se a memória estiver vazia, aloca-se na posição 0
        if (len(self.espacosOcupados) == 0):
            print('Lista vazia, insere-se o job no início')
            return True, 0

        # Depois vejo se há espaço livre entre a posição 0 e o início do primeiro espaço ocupado
        if(self.espacosOcupados[0][0] >= qtdMem):
            print('Lista não vazia, mas insere-se o job no início')
            return True, 0

        # Depois vejo se há espaço disponível entre 2 jobs
        if(len(self.espacosOcupados) >= 2):
            for i in range(len(self.espacosOcupados) - 1):
                if(self.espacosOcupados[i + 1][0] - self.espacosOcupados[i][1]) > qtdMem:
                    print('Insere-se o  job entre as posições ' + str(self.espacosOcupados[i][1]) + ' e ' + str(self.espacosOcupados[i + 1][0]))
                    return True, (self.espacosOcupados[i][1] + 1)

        # Por fim vejo se há espaço disponível após o job que ocupa a última posição da ordem
        if(self.tamanho - 1 - self.espacosOcupados[len(self.espacosOcupados) - 1][1]) >= qtdMem:
            print('Insere-se o job ao final da memória, a partir da posição ' + str(self.espacosOcupados[len(self.espacosOcupados) - 1][1] + 1))
            return True, (self.espacosOcupados[len(self.espacosOcupados) - 1][1] + 1)

        # Se todos as condições anteriores falharem, significa que não há espaço para o job que se quer alocar
        return False, None

    def alocarJobDaFila(self):
        # O elemento de maior prioridade encontra-se na última posição da fila, posição (len(self.fila) - 1)
        # Calcula-se primeiro quanta memória será necessária para alocar todos os segmentos ativos do job
        memoriaNecessaria = 0
        for segm in self.fila[len(self.fila) - 1].segmentosAtivos:
            memoriaNecessaria += self.fila[len(self.fila) - 1].listaSegmentos[segm].memoria
        print('\r\nQuantidade de memória requerida para alocar o job ' + str(self.fila[len(self.fila) - 1].nome) + ' --> ' + str(memoriaNecessaria))
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
            self.fila.pop()

    def alocarNovoJob(self, job):
        self.fila.insert(0, job)

    def mostrarSegmentTable(self):
        print(self.segmentTable)

    def mostrarEspacosOcupados(self):
        print(self.espacosOcupados)

    def liberarJob(self, nomeDoJob):
        # Primeiro consulta-se a segmentTable para ver quais posições são pertinentes ao job que ser quer remover
        chavesADeletar = []
        for key in self.segmentTable.keys():
            if nomeDoJob in key:
                # Liberando o espaço
                for i in range(len(self.espacosOcupados)):
                    if(self.espacosOcupados[i][0] == self.segmentTable[key][0]):
                        del self.espacosOcupados[i]
                        break

                # Verificando quais arquivos devem ser removidos da memória
                nomesDeArquivosParaDeletar = []
                for nomeArquivo in self.fileTable.keys():
                    if(nomeDoJob in self.fileTable[nomeArquivo][1]):
                        if len(self.fileTable[nomeArquivo][1]) == 1:
                            nomesDeArquivosParaDeletar.append(nomeArquivo)
                        else:
                            indiceParaRemover = self.fileTable[nomeArquivo][1].index(nomeDoJob)
                            del(self.fileTable[nomeArquivo][1][indiceParaRemover])

                # Para atualizar a tabela de segmentos
                chavesADeletar.append(key)  # Não posso deletar dentro do laço porque estou iterando sobre as chaves

        for key in chavesADeletar:
            del self.segmentTable[key]

    def verificarPresencaDeSegmento(self, nomeDoJob, numeroDoSegmento):
        if(str(nomeDoJob) + str(numeroDoSegmento)) in self.segmentTable.keys():
            return True
        else:
            return False

    def carregarArquivoDoDisco(self, nomeDoArquivo, jobSolicitante, disco):
        # Retorna-se True caso um novo arquivo seja inserido na memória com sucesso ou já esteja em memória e o job solicitante pode acessar esse arquivo
        # Retorna-se False se o job solicitante não puder acessar o arquivo ou o arquivo não existir no disco

        # Arquivo não presente no disco
        if nomeDoArquivo not in disco.arquivos.keys():
            return False

        # Job solicitante não tem acesso ao arquivo
        if ('Public' not in disco.arquivos[nomeDoArquivo][1]) and (jobSolicitante not in disco.arquivos[nomeDoArquivo][1]):
            return False

        # Arquivo não presente ainda em memória
        if nomeDoArquivo not in self.fileTable.keys():
            if('Public' in disco.arquivos[nomeDoArquivo][1]):
                dono = 'Public'
            else:
                dono = jobSolicitante
            self.fileTable[nomeDoArquivo] = [dono, [jobSolicitante]]
            return True

        # Arquivo presente na memória e público (para os casos que jobs simultâneos acessem o arquivo)
        if(self.fileTable[nomeDoArquivo][0] == 'Public'):
            self.fileTable[nomeDoArquivo][1].append(jobSolicitante)
            return True
