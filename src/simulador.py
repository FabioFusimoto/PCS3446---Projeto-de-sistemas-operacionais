import texttable
import os.path
import random
from disco import HD
from dispositivos import DeviceManager
from jobs import Job, Segmento, lerJobDoArquivo, montarTabelaDeJobs
from memoria import RAM
from processador import CPU


class SIM:
    def __init__(self, duracaoSimulacao, numMaximoDeJobs, listaDeJobs, instantesDeSubmissao, tamanhoDaMemoria, tamanhoDoDisco, tAcessoAoDisco, nomeDosArquivos, timeSliceProcessador, dispositivos):
        # Parâmetros de simulação
        self.instanteAtual = 0
        self.quantidadeDeJobsAlocados = 0
        self.duracao = duracaoSimulacao
        self.numMaximoDeJobs = numMaximoDeJobs

        # Os jobs que chegam não necessariamente serão submetidos
        # Caso ultrapasse o limite de jobs, os mesmos terão de esperar
        self.jobs = montarTabelaDeJobs(listaDeJobs)
        self.instantesDeSubmissao = instantesDeSubmissao

        # Lista com os índices dos jobs que já foram submetidos
        self.jobsSubmetidos = []

        # Lista com os índices dos jobs que já foram submetidos e finalizados
        self.jobsFinalizados = []
        for job in self.jobs:
            segmentosAtivos = [0]  # Por convenção, o segmento raiz sempre deve estar ativo
            segmAtual = 0
            while True:
                if(len(job.arvore[segmAtual][1]) == 0):
                    # Não há mais nós filho
                    break
                else:
                    # Sorteia um nó filho e adiciona à lista de ativos
                    segmAtual = random.choice(job.arvore[segmAtual][1])
                    segmentosAtivos.append(segmAtual)
            job.definirSegmentosAtivos(segmentosAtivos)

        # Calculando, para cada segmento de cada job, os instantes em que ocorre E/S ou acesso ao disco
        # instantesDeES[nomeDoJob] = [(instante, nomeDoDispositivo)]
        self.instantesDeES = {}
        # instantesDeAcessoAoDisco[nomeDoJob] = [(instante, nomeDoArquivo)]
        self.instantesDeAcessoAoDisco = {}
        for job in self.jobs:
            # A base de tempo deve ser atualizada quando se salta de um segmento para outro
            baseDeTempo = 0
            self.instantesDeES[job.nome] = []
            self.instantesDeAcessoAoDisco[job.nome] = []
            for s in job.segmentosAtivos:
                duracaoSegm = job.listaSegmentos[s].tCPU

                # Requisições de entrada e saída
                dispositivoES = job.listaSegmentos[s].nomeE_S
                qtdES = job.listaSegmentos[s].qtdE_S
                if(dispositivoES != 'Nenhum'):
                    for n in range(qtdES):
                        instanteCorrigido = int(baseDeTempo + ((n + 1) * (duracaoSegm / (qtdES + 1))))
                        self.instantesDeES[job.nome].append((instanteCorrigido, dispositivoES))

                # Requisições de acesso ao disco
                for k in range(job.listaSegmentos[s].qtdArquivos):
                    # Primeiro aplica-se a correção da base de tempo
                    for i in range(len(job.listaSegmentos[s].instantesDeAcesso)):
                        job.listaSegmentos[s].instantesDeAcesso[i] += baseDeTempo

                    # Depois os valores são inseridos no dicionário
                    for instante in job.listaSegmentos[s].instantesDeAcesso:
                        self.instantesDeAcessoAoDisco[job.nome].append((instante, job.listaSegmentos[s].nomeDosArquivos[k]))

                baseDeTempo += duracaoSegm

        # Agora irei juntar os instantes e gerar listas de momentos de interrupção de processamento
        # interrupcoes[nomeDoJob] = [(t, 'D' para disco 'ES' para E/S, dispositivo/nomeDoArquivo)]
        self.interrupcoes = {}
        for job in self.jobs:
            self.interrupcoes[job.nome] = []

            # Interrupções de E/S
            for IES in self.instantesDeES[job.nome]:
                self.interrupcoes[job.nome].append((IES[0], 'ES', IES[1]))

            # Interrupções de acesso ao disco
            for ID in self.instantesDeAcessoAoDisco[job.nome]:
                self.interrupcoes[job.nome].append((ID[0], 'D', ID[1]))

            self.interrupcoes[job.nome].sort(key=lambda tup: tup[0])

        # print('Interrupções ordenadas por instante:')
        # print(self.interrupcoes)

        # Instanciando os demais componentes
        self.memoria = RAM(tamanho=tamanhoDaMemoria)
        self.disco = HD(tamanho=tamanhoDoDisco, numCiclos=tAcessoAoDisco, listaDeNomes=nomeDosArquivos)
        self.processador = CPU(timeSlice=timeSliceProcessador)
        self.GD = DeviceManager(dispositivos=dispositivos)

        # Criando o log de simulação
        self.log = texttable.Texttable(max_width=100)
        self.log.add_row(['Instante', 'Tags', 'Tipo', 'Mensagem'])
        self.log.set_cols_align(['c', 'c', 'c', 'c'])
        self.log.set_cols_width([7, 15, 5, 80])

    def avancarSimulacao(self):
        # Retorna True se a simulação tiver que continuar e False caso tenha que acabar
        if(self.instanteAtual == self.duracao):
            return False, []
        else:
            eventos = []
            # 1) Verifica se até o instante atual ocorre a chegada de algum job e os submete quando o limite não for atingido
            for i in range(len(self.jobs)):
                # Verificando se o limite de jobs
                if (i not in self.jobsSubmetidos) and (i not in self.jobsFinalizados) and (self.instantesDeSubmissao[i] <= self.instanteAtual):
                    if(self.quantidadeDeJobsAlocados < self.numMaximoDeJobs):
                        self.memoria.alocarNovoJob(self.jobs[i])
                        self.log.add_row([str(self.instanteAtual), ['M'], 'JIF', 'Job  ' + self.jobs[i].nome + ' inserido na fila de acesso à memória'])
                        self.quantidadeDeJobsAlocados += 1
                        self.jobsSubmetidos.append(i)
                        eventos.append('JIF')
                    elif(self.instantesDeSubmissao[i] == self.instanteAtual):
                        self.log.add_row([str(self.instanteAtual), ['M'], 'JNIF', 'Job  ' + self.jobs[i].nome + ' chegou mas não foi inserido na fila de acesso à memória pois o limite de jobs foi atingido'])
                        eventos.append('JNIF')

            # 2) Aloca-se primeiro job (dentre os já submetidos) da fila do gerenciador de memória na memória, se houver espaço e insere-se o job na fila do processador
            memoriaFoiAlocada, nomeDoJob = self.memoria.alocarJobDaFila()
            if(memoriaFoiAlocada):
                jobAAlocar = None
                for index in self.jobsSubmetidos:
                    if self.jobs[index].nome == nomeDoJob:
                        jobAAlocar = self.jobs[index]
                        break
                instantesDeInterrupcao = []
                for i in range(len(self.interrupcoes[nomeDoJob])):
                    instantesDeInterrupcao.append(self.interrupcoes[nomeDoJob][i][0])
                self.processador.adicionarNovoJob(job=jobAAlocar, instantesE_S=instantesDeInterrupcao)
                self.log.add_row([str(self.instanteAtual), ['M', 'C'], 'RA', 'Recursos alocados para o job ' + nomeDoJob])
                eventos.append('RA')
                # print('Alocou-se o job ' + nomeDoJob + ' com as interrupções nos seguintes instantes: ' + str(instantesDeInterrupcao))

            # 3) Atualiza-se o estado do disco, verificando se um novo acesso é iniciado ou o acesso
            # corrente é finalizado e esse fato é informado ao processador
            atualizacaoNoDisco, nomeDoJob, mensagem, tipo, nomeDoArquivo = self.disco.atualizar()
            if(atualizacaoNoDisco):
                nomeDoJob = nomeDoJob
                if(tipo == 'F'):
                    self.processador.alternarParaModoPronto(nomeJob=nomeDoJob)
                    naoUsoEssaVariavel = self.memoria.carregarArquivoDoDisco(nomeDoArquivo=nomeDoArquivo, jobSolicitante=nomeDoJob, disco=self.disco)
                    self.log.add_row([str(self.instanteAtual), ['D', 'M'], 'ADF', 'Arquivo ' + nomeDoArquivo + ' trazido do disco para a memória mediante solicitação do job ' + nomeDoJob])
                    eventos.append('ADF')
                elif(tipo == 'A'):
                    self.log.add_row([str(self.instanteAtual), ['D'], 'ADI', mensagem])
                    eventos.append('ADI')

            # 4) Atualiza-se o estado do gerenciador de dispositivos, verificando se houve término de acesso
            # a algum dispositivo de E/S, informando este fato ao processador
            atualizacaoDeES, mensagem, ESIniciadas, ESFinalizadas = self.GD.atualizar()
            if(atualizacaoDeES):
                self.log.add_row([str(self.instanteAtual), ['GD'], 'AGD', mensagem])
                eventos.append('AGD')
                for es in ESFinalizadas:
                    self.processador.alternarParaModoPronto(nomeJob=es[0])

            # 5) Roda-se a CPU durante um intervalo t e verifica-se se ocorreu algum dos seguintes eventos:
            atualizacaoDeCPU, mensagem, tipo, nomeDoJob = self.processador.atualizar()
            if(atualizacaoDeCPU):
                if(tipo == 'TS'):
                    self.log.add_row([str(self.instanteAtual), ['C'], 'FTS', mensagem])
                    eventos.append('FTS')
                elif(tipo == 'F'):
                    # job finalizado, logo deve ser removido da lista de jobs correntes
                    index = None
                    for i in range(len(self.jobs)):
                        if(self.jobs[i].nome == nomeDoJob):
                            index = i
                            break
                    self.jobsFinalizados.append(index)
                    self.memoria.liberarJob(nomeDoJob=nomeDoJob)
                    posicaoParaDeletar = self.jobsSubmetidos.index(index)
                    del self.jobsSubmetidos[posicaoParaDeletar]
                    self.quantidadeDeJobsAlocados -= 1
                    filaProcessador = []
                    for elemento in self.processador.fila:
                        filaProcessador.append(elemento[0])
                    # print('\r\nJob ' + nomeDoJob + ' finalizado no instante ' + str(self.instanteAtual))
                    # print('Job que passou a ser executado: ' + str(self.processador.jobAtual))
                    # print('Jobs remanescentes na fila do processador: ' + str(filaProcessador))
                    # print('Jobs submetidos: ' + str(self.jobsSubmetidos))
                    # print('Jobs finalizados: ' + str(self.jobsFinalizados))
                    self.log.add_row([str(self.instanteAtual), ['C'], 'FJ', mensagem])
                    eventos.append('FJ')
                elif(tipo == 'ES'):
                    # Para o processador, disco e E/S são a mesma coisa, é preciso primeiro saber qual dos dois se referencia
                    # Verifica-se o primeiro instante de interrupção programado, remove-o da lista e decide-se se ele é Disco ou E/S
                    # print('\r\nInterrupção do job ' + nomeDoJob)
                    # print('Lista de interrupções pendentes: ' + str(self.interrupcoes))
                    interrupcao = self.interrupcoes[nomeDoJob].pop(0)

                    # Assume-se que um job não pode solicitar disco e E/S no mesmo instante
                    if(interrupcao[1] == 'D'):
                        # Interrupção de acesso ao disco
                        acessoValidoAoDisco, mensagem = self.disco.validarAcesso(nomeDoJob=nomeDoJob, nomeDoArquivo=interrupcao[2])
                        if(acessoValidoAoDisco):
                            acesso, mensagem = self.disco.solicitarAcessoAoDisco(nomeDoJob=nomeDoJob, nomeDoArquivo=interrupcao[2])
                            self.log.add_row([self.instanteAtual, ['D'], 'AVD', mensagem])
                            eventos.append('AVD')
                        else:
                            # Acesso ilegal ao arquivo, encerra-se o job solicitante
                            # Remove-se também os instantes de E/S, acesso ao disco e interrupções (que é a junção de ambos)
                            self.processador.encerrarJob(nomeDoJob=nomeDoJob)
                            self.memoria.liberarJob(nomeDoJob=nomeDoJob)

                            indiceDoJob = None
                            for i in range(len(self.jobs)):
                                if(self.jobs[i].nome == nomeDoJob):
                                    indiceDoJob = i

                            # Inserindo na lista de finalizados
                            self.jobsFinalizados.append(indiceDoJob)

                            # Removendo da lista de ativos
                            del self.jobsSubmetidos[self.jobsSubmetidos.index(indiceDoJob)]

                            # Removendo as interrupções da lista, se houver
                            if(nomeDoJob in self.interrupcoes.keys()):
                                del self.interrupcoes[nomeDoJob]
                            if(nomeDoJob in self.instantesDeES.keys()):
                                del self.instantesDeES[nomeDoJob]
                            if(nomeDoJob in self.instantesDeAcessoAoDisco.keys()):
                                del self.instantesDeAcessoAoDisco[nomeDoJob]

                            # atualizando a quantidade de jobs alocados
                            self.quantidadeDeJobsAlocados -= 1

                            self.log.add_row([str(self.instanteAtual), ['D', 'M', 'C'], 'AID', 'Job ' + nomeDoJob + ' solicitou acesso ilegal ao arquivo ' + interrupcao[2] + ' e foi finalizado'])
                            eventos.append('AID')
                    else:
                        self.GD.solicitarES(nomeDoJob=nomeDoJob, nomeDoDispositivo=interrupcao[2])
                        self.log.add_row([str(self.instanteAtual), ['GD'], 'IDisp', 'Job ' + nomeDoJob + ' solicitou acesso ao dispositivo ' + interrupcao[2]])
                        eventos.append('IDisp')

                    # print('\r\nInterrupção no instante ' + str(self.instanteAtual) + ' Interrupções remanescentes:')
                    # print(self.interrupcoes)

            self.instanteAtual += 1
            return True, eventos

    def mostrarLog(self):
        print('\r\nLog de simulação')
        print(self.log.draw())

    def inserirLogNoArquivo(self, nomeDoArquivo):
        f = open(nomeDoArquivo, 'w+')
        f.write(self.log.draw())

    def mostrarInstantesDeInterrupcao(self):
        interrupcoes = []
        for key in self.interrupcoes.keys():
            for interr in self.interrupcoes[key]:
                interrupcoes.append([key, interr[0], interr[1], interr[2]])

        t = texttable.Texttable()
        t.add_row(['Job', 'Instante', 'Tipo', 'Nome do dispositivo ou arquivo a acessar'])
        for i in interrupcoes:
            t.add_row(i)
        print(t.draw())

    def mostrarEstado(self):
        print('\r\n=====Jobs=====')
        t = texttable.Texttable()
        t.add_row(['Job', 'Estado'])
        for i in range(len(self.jobs)):
            estado = None
            if (i in self.jobsSubmetidos) and (i not in self.jobsFinalizados):
                estado = 'Submetido'
            elif(i in self.jobsFinalizados):
                estado = 'Finalizado'
            else:
                estado = 'Ainda não submetido'
            t.add_row([self.jobs[i].nome, estado])
        print(t.draw())

        print('\r\n=====Memória=====')
        self.memoria.mostrarEspacosOcupados()
        self.memoria.mostrarSegmentTable()
        self.memoria.mostrarFileTable()

        print('\r\n=====Disco=====')
        self.disco.exibirArquivos()
        self.disco.exibirEstado()

        print('\r\n=====Dispositivos=====')
        self.GD.mostrarEstado()

        print('\r\n=====Interrupções pendentes=====')
        self.mostrarInstantesDeInterrupcao()
