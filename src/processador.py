import texttable


class CPU:
    def __init__(self, timeSlice):
        # Quanto tempo cada job tem para ser executado
        self.timeSlice = timeSlice

        # Fila de prioridade com elementos da forma [nome do job, ciclos remanescentes, estado, quantidade de ciclos já executados]
        # Estado pode ter os valores: 'P' - pronto, 'ES' - a espera de E/S
        self.fila = []

        # Instantes em que os jobs vão requerir E/S ou acesso ao disco instantesE_S[nomeDoJob] = [t1,t2,...,tn] --> sempre em ordem crescente
        self.instantesE_S = {}

        # Nome do job sendo atualmente executado
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

        # print('Job ' + job.nome + ' inserido na fila do processador')

    def escalonarJob(self):
        # Retorna False se não houver job para escalonar
        if(len(self.fila) == 0):
            self.timeSliceJobAtual = self.timeSlice
            self.jobAtual = None
            self.ciclosParaConcluirJobAtual = None
            self.ciclosExecutadosNoTotal = None
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
        instanteDeInterrupcao = self.instantesE_S[self.jobAtual].pop(0)  # Remove o instante da lista
        self.inserirJobNoFinalDaFila(nomeDoJob=self.jobAtual, ciclosRemanescentes=self.ciclosParaConcluirJobAtual, estado='ES',
                                     qtdCiclosJaExecutados=instanteDeInterrupcao)
        self.timeSliceJobAtual = self.timeSlice
        self.jobAtual = None
        self.ciclosParaConcluirJobAtual = None
        self.ciclosExecutadosNoTotal = None

    def alternarParaModoPronto(self, nomeJob):
        """Função a ser chamada pelo gerenciador de disco ou gerenciador de E/S para indicar o fim de operação de E/S"""
        for i in range(len(self.fila)):
            if self.fila[i][0] == nomeJob:
                self.fila[i][2] = 'P'
                break

    def encerrarJob(self, nomeDoJob):
        """Encerra o job atualmente com o nome fornecido e remove os instantes de E_S da lista"""
        if(nomeDoJob in self.instantesE_S.keys()):
            del self.instantesE_S[nomeDoJob]
        if(nomeDoJob == self.jobAtual):
            self.jobAtual = None
            self.timeSliceJobAtual = self.timeSlice
            self.ciclosParaConcluirJobAtual = None
            self.ciclosExecutadosNoTotal = 0

        # Remover o job da fila
        for index in range(len(self.fila)):
            if self.fila[index][0] == nomeDoJob:
                del self.fila[index]
                break

    def atualizar(self):
        """Atualiza o estado do processamento, verificando se o job atual finalizou seu processamento, se o job requer E/S e se houve fim de time slice"""
        # Possibilidades de valor a se retornar (True/False, Mensagem, Tipo de evento):
        # (False, None, None, None) se não houver nenhuma alteração
        # (True, 'Job alocado da fila', 'A', None) se for a primeira vez que um job for alocado, isto é, na situação inicial
        # (True, 'Execução do job nomeDoJob foi finalizada', 'F', nome do job finalizado)
        # (True, 'Fim do time slice para o job nomeDoJob', 'TS', None)
        # (True, 'Job nomeDoJob solicitou E/S', 'ES', nome do job que solicita E/S)

        haJobsProntosNaLista = False
        for job in self.fila:
            if(job[2] == 'P'):
                haJobsProntosNaLista = True

        if(self.jobAtual is None):
            if(haJobsProntosNaLista):
                # Não há jobs correntes mas há jobs prontos na fila (situação inicial por exemplo)
                escalonar = self.escalonarJob()
                return True, ('Job ' + str(self.jobAtual) + ' alocado da fila'), 'A', None
            else:
                # Não há job corrente e nenhum job pronto na fila
                return False, None, None, None

        self.ciclosExecutadosNoTotal += 1
        self.ciclosParaConcluirJobAtual -= 1
        self.timeSliceJobAtual -= 1

        if(self.ciclosParaConcluirJobAtual == 0):
            # Término do processamento
            jobEncerrado = self.jobAtual
            mensagemDeRetorno = ('Execução do job ' + jobEncerrado + ' foi finalizada')
            self.encerrarJob(self.jobAtual)
            escalonar = self.escalonarJob()
            if(not escalonar):
                mensagemDeRetorno += '. Não há nenhum outro job pronto para execução'
            else:
                mensagemDeRetorno += '. Alterna-se para a execução do job ' + self.jobAtual
            return True, mensagemDeRetorno, 'F', jobEncerrado
        elif((self.jobAtual in self.instantesE_S.keys()) and (self.ciclosExecutadosNoTotal in self.instantesE_S[self.jobAtual])):
            # Solicitação de E/S
            jobSolicitante = self.jobAtual
            mensagemDeRetorno = ('Job ' + jobSolicitante + ' solicitou E/S')
            self.alternarParaModoE_S()
            escalonar = self.escalonarJob()
            if(not escalonar):
                mensagemDeRetorno += '. Não há nenhum outro job pronto para execução'
            else:
                mensagemDeRetorno += '. Alterna-se para a execução do job ' + self.jobAtual
            return True, mensagemDeRetorno, 'ES', jobSolicitante
        elif(self.timeSliceJobAtual == 0):
            # Fim do timeSlice
            mensagemDeRetorno = 'Fim do time slice do job ' + self.jobAtual
            jobAnterior = self.jobAtual
            estado = 'P'
            if(self.jobAtual in self.instantesE_S.keys()) and (self.ciclosExecutadosNoTotal in self.instantesE_S[self.jobAtual]):
                estado = 'ES'
            self.inserirJobNoFinalDaFila(nomeDoJob=self.jobAtual, ciclosRemanescentes=self.ciclosParaConcluirJobAtual,
                                         estado=estado, qtdCiclosJaExecutados=self.ciclosExecutadosNoTotal)
            escalonar = self.escalonarJob()
            if(jobAnterior == self.jobAtual):
                # Para o caso em que ocorre o fim do time slice, mas o job que toma conta do processador é o mesmo que no time slice anterior
                return False, None, None, None
            if(not escalonar):
                mensagemDeRetorno += '. Não há nenhum outro job pronto para execução'
            else:
                mensagemDeRetorno += '. Alterna-se para a execução do job ' + self.jobAtual
            return True, mensagemDeRetorno, 'TS', None
        else:
            # Nenhuma alteração em relação ao ciclo anterior
            return False, None, None, None

    def mostrarEstadoAtual(self):
        print('\r\nEstado atual do processador')
        t = texttable.Texttable()
        t.add_row(['Job atual', 'Instantes de interrupção do job atual', 'Ciclos remanescentes nesse time slice', 'Ciclos já executados nesse time slice', 'Ciclos para finalizar o job atual'])
        t.add_row([self.jobAtual, self.instantesE_S[self.jobAtual], self.timeSliceJobAtual, self.ciclosExecutadosNoTotal, self.ciclosParaConcluirJobAtual])
        print(t.draw())

    def mostrarFila(self):
        print('\r\nJobs na fila')
        t = texttable.Texttable()
        t.add_row(['Nome', 't para terminar a execução', 'Estado', 'Ciclos já executados', 'Instantes de interrupção'])

        for job in self.fila:
            t.add_row([job[0], job[1], job[2], job[3], self.instantesE_S[job[0]]])
        print(t.draw())
