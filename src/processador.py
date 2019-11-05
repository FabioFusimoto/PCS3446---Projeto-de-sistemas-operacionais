class CPU:
    def __init__(self, timeSlice):
        # Quanto tempo cada job tem para ser executado
        self.timeSlice = timeSlice

        # Fila de prioridade com elementos da forma [nome do job, ciclos remanescentes, estado, quantidade de ciclos já executados]
        # Estado pode ter os valores: 'P' - pronto, 'ES' - a espera de E/S
        self.fila = []

        # Instantes em que os jobs vão requerir E/S ou acesso ao disco instantesE_S[nomeDoJob] = [t1,t2,...,tn] --> sempre em ordem crescente
        self.instantesE_S = {}

        # Número do job sendo atualmente executado
        self.jobAtual = None

        # Quantos t o job atual ainda permanecerá ocupando o processador
        self.timeSliceJobAtual = None

        # Quantos t o job atual ainda precisa para finalizar seu processamento
        self.ciclosParaConcluirJobAtual = None

        # Quantos t o job atual já tomou da CPU no total, não só no time slice corrente (necessário para sincronizar os pedidos de E/S)
        self.ciclosExecutadosNoTotal = 0

    def adicionarNovoJob(self, job, instantesE_S):
        # job é um objeto da classe Job, definida no arquivo jobs

        # Contabilizando o tCPU total para o job
        tTotal = 0
        for segm in job.segmentosAtivos:
            tTotal += job.listaSegmentos[segm].tCPU

        self.fila.insert(0, [job.nome, tTotal, 'P', 0])
        self.instantesE_S[job.nome] = instantesE_S

    def escalonarJob(self):
        # Retorna False se não houver job para escalonar
        if(len(self.fila) == 0):
            return False

        # Verificar qual o primeiro job da fila cujo estado é 'P'
        # Se o job não estiver pronto no momento que se faz a verificação, ele vai para o final da fila
        qtdJobsVerificados = 0
        jobAEscalonar = None
        while(qtdJobsVerificados < len(self.fila)):
            jobAEscalonar = self.fila.pop()
            if(jobAEscalonar[2] == 'P'):
                break
            else:
                self.fila.insert(0, jobAEscalonar)
                jobAEscalonar = None
                qtdJobsVerificados += 1

        if jobAEscalonar is None:
            return False

        # Escalonando o job encontrado
        self.timeSliceJobAtual = self.timeSlice
        self.jobAtual = jobAEscalonar[0]
        self.ciclosParaConcluirJobAtual = jobAEscalonar[1]
        self.ciclosExecutadosNoTotal = jobAEscalonar[3]
        return True

    def inserirJobNoFinalDaFila(self, nomeDoJob, ciclosRemanescentes, estado, qtdCiclosJaExecutados):
        self.fila.insert(0, [nomeDoJob, ciclosRemanescentes, estado, qtdCiclosJaExecutados])

    def alternarParaModoE_S(self):
        """Atualiza o job corrente para o modo E/S e o insere no final da fila. Salva-se quantos ciclos ainda faltam para executar e escalona-se o próximo job"""
        # print('\r\n=====Antes do escalonamento=====')
        # self.mostrarEstadoAtual()
        # self.mostrarFila()
        instanteDeInterrupcao = self.instantesE_S[self.jobAtual].pop(0)  # Remove o instante da lista
        self.inserirJobNoFinalDaFila(nomeDoJob=self.jobAtual, ciclosRemanescentes=self.ciclosParaConcluirJobAtual, estado='ES',
                                     qtdCiclosJaExecutados=instanteDeInterrupcao)
        # print('O job ' + self.jobAtual + ' entrou no modo E/S')

    def alternarParaModoPronto(self, nomeJob):
        """Função a ser chamada pelo gerenciador de disco ou gerenciador de E/S para indicar o fim de operação de E/S"""
        for i in range(len(self.fila)):
            if self.fila[i][0] == nomeJob:
                self.fila[i][2] = 'P'
                break

    def encerrarJobAtual(self):
        """Encerra o job atualmente em execução e remove os instantes de E_S da lista"""
        del self.instantesE_S[self.jobAtual]
        self.jobAtual = None
        self.timeSliceJobAtual = self.timeSlice
        self.ciclosParaConcluirJobAtual = None
        self.ciclosExecutadosNoTotal = 0

    def atualizar(self):
        """Atualiza o estado do processamento, verificando se o job atual finalizou seu processamento, se o job requer E/S e se houve fim de time slice"""
        # Possibilidades de valor a se retornar:
        # (False, None) se não houver nenhuma alteração
        # (True, 'Job alocado da fila') se for a primeira vez que um job for alocado, isto é, na situação inicial
        # (True, 'Nenhum job pronto para ser escalonado')
        # (True, 'Execução do job nomeDoJob foi finalizada')
        # (True, 'Fim do time slice para o job nomeDoJob')
        # (True, 'Job nomeDoJob solicitou E/S)'

        haJobsProntosNaLista = False
        for job in self.fila:
            if(job[2] == 'P'):
                haJobsProntosNaLista = True

        if(self.jobAtual is None):
            if(haJobsProntosNaLista):
                # Situação inicial, primeira inicialização do processador
                escalonar = self.escalonarJob()
                return True, ('Job ' + str(self.jobAtual) + ' alocado da fila')
            else:
                return False, None

        self.ciclosExecutadosNoTotal += 1
        self.ciclosParaConcluirJobAtual -= 1
        self.timeSliceJobAtual -= 1

        if(self.ciclosParaConcluirJobAtual == 0):
            # Término do processamento
            mensagemDeRetorno = ('Execução do job ' + self.jobAtual + ' foi finalizada')
            self.encerrarJobAtual()
            escalonar = self.escalonarJob()
            if(not escalonar):
                mensagemDeRetorno += '. Não há nenhum outro job pronto para execução'
            else:
                mensagemDeRetorno += '. Alterna-se para a execução do job ' + self.jobAtual
            return True, mensagemDeRetorno
        elif(self.ciclosExecutadosNoTotal in self.instantesE_S[self.jobAtual]):
            # Solicitação de E/S
            mensagemDeRetorno = ('Job ' + self.jobAtual + ' solicitou E/S')
            self.alternarParaModoE_S()
            escalonar = self.escalonarJob()
            if(not escalonar):
                mensagemDeRetorno += '. Não há nenhum outro job pronto para execução'
            else:
                mensagemDeRetorno += '. Alterna-se para a execução do job ' + self.jobAtual
            # print('\r\n=====Depois do escalonamento devido a E/S=====')
            # self.mostrarEstadoAtual()
            # self.mostrarFila()
            return True, mensagemDeRetorno
        elif(self.timeSliceJobAtual == 0):
            # Fim do timeSlice
            mensagemDeRetorno = 'Fim do time slice do job ' + self.jobAtual
            jobAnterior = self.jobAtual
            estado = 'P'
            if(self.ciclosExecutadosNoTotal in self.instantesE_S[self.jobAtual]):
                estado = 'ES'
            self.inserirJobNoFinalDaFila(nomeDoJob=self.jobAtual, ciclosRemanescentes=self.ciclosParaConcluirJobAtual,
                                         estado=estado, qtdCiclosJaExecutados=self.ciclosExecutadosNoTotal)
            escalonar = self.escalonarJob()
            if(jobAnterior == self.jobAtual):
                # Para o caso em que ocorre o fim do time slice, mas o job que toma conta do processador é o mesmo que no time slice anterior
                return False, None
            if(not escalonar):
                mensagemDeRetorno += '. Não há nenhum outro job pronto para execução'
            else:
                mensagemDeRetorno += '. Alterna-se para a execução do job ' + self.jobAtual
            return True, mensagemDeRetorno
        else:
            # Nenhuma alteração em relação ao ciclo anterior
            return False, None

    def mostrarEstadoAtual(self):
        print('\r\n>>>>>Estado atual<<<<<')
        print('Job atual: ' + self.jobAtual)
        print('Instantes de E/S: ' + str(self.instantesE_S[self.jobAtual]))
        print('Ciclos que o job atual ainda tem direito: ' + str(self.timeSliceJobAtual))
        print('Ciclos que o job atual já executou no total: ' + str(self.ciclosExecutadosNoTotal))
        print('Ciclos remanescentes para finalizar o jobAtual: ' + str(self.ciclosParaConcluirJobAtual))

    def mostrarFila(self):
        print('\r\n>>>>>Jobs na fila<<<<<')
        i = 0
        for job in self.fila:
            print('\r\nPrioridade ' + str(i))
            print('Nome: ' + job[0])
            print('Ciclos remanescente pra terminar sua execução: ' + str(job[1]))
            print('Estado: ' + job[2])
            print('Ciclos já executados: ' + str(job[3]))
            print('Instantes que requerem E/S: ' + str(self.instantesE_S[job[0]]))
            i += 1
