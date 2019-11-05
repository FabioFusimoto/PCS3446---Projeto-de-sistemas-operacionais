import os.path


class HD:
    def __init__(self, tamanho, numCiclos):
        # indica se algum job está utilizando o disco nesse instante
        self.emUso = False

        # indica qual job está fazendo uso do disco, se houver
        self.jobUtilizandoODisco = None

        # indica o nome do arquivo sendo atualmente acessado no disco
        self.arquivoSendoAcessado = None

        # indica quantos 't' demora para acessar um arquivo no disco
        self.numCiclos = numCiclos

        # indica quantos ciclos ainda faltam para completar o acesso atual ao disco
        self.contadorRegressivo = 0

        # arquivos[nome] = [tamanho, [lista de jobs que podem acessar o arquivo]] - a lista de jobs pode incluir 'Public' indicando que é acessível a todos os jobs
        self.arquivos = {}

        # Guarda a posiçao do último arquivo que foi inserido no disco
        self.ultimoEspacoOcupado = 0

        # Fila com o nome dos jobs que desejam acessar arquivos do disco. O job na última posição da fila tem maior prioridade
        # Constituído de elementos do tipo [nomeDoJob, nomeDoArquivo]
        self.fila = []

    def inicializar(self, listaDeNomes):
        f = open(os.path.split(os.path.dirname(__file__))[0] + '/txt/files/arquivos.txt', 'r')
        linhas = f.readlines()
        f.close()
        for l in linhas:
            linha = l.split('\n')[0]  # serve para eliminar o \n ao final de cada linha
            nomeArquivo = linha.split(',')[0]
            if(nomeArquivo in listaDeNomes):
                tamanho = linha.split(',')[1]
                listaDeDonos = []
                for i in range(2, len(linha.split(','))):
                    listaDeDonos.append(linha.split(',')[i])
                self.adicionarArquivo(nome=nomeArquivo, tamanho=int(tamanho), donos=listaDeDonos)

    def adicionarArquivo(self, nome, tamanho, donos):
        if nome not in self.arquivos.keys():
            self.arquivos[nome] = [tamanho, donos]
            self.ultimoEspacoOcupado += tamanho
            return True
        else:
            return False

    def solicitarAcessoAoDisco(self, nomeDoJob, nomeDoArquivo):
        # Verifica-se se dado job tem acesso ao arquivo
        # Retorna-se True se a solicitação for válida e True caso contrário
        # Retorna uma mensagem de erro caso o primeiro valor seja 'False'

        # Arquivo inexistente
        if nomeDoArquivo not in self.arquivos.keys():
            return False, ('O arquivo ' + nomeDoArquivo + ' não existe')

        # Acesso proibido
        if ('Public' not in self.arquivos[nomeDoArquivo][1]) and (nomeDoJob not in self.arquivos[nomeDoArquivo][1]):
            return False, ('O job ' + nomeDoJob + ' não tem acesso ao arquivo ' + nomeDoArquivo)

        # Acesso permitido, insere-se a solicitação de acesso na fila
        self.fila.insert(0, [nomeDoJob, nomeDoArquivo])
        return True, ('Job ' + nomeDoJob + ' solicitou acesso ao arquivo ' + nomeDoArquivo)

    def acessarDisco(self):
        # Realiza o acesso de maior prioridade ao disco. Inicia a contagem regressiva
        # Retorna True se o acesso for iniciado e False caso contrário

        if (len(self.fila) == 0) or (self.emUso):
            return False

        self.emUso = True
        self.contadorRegressivo = self.numCiclos
        primeiroDaFila = self.fila.pop()
        self.jobUtilizandoODisco, self.arquivoSendoAcessado = primeiroDaFila[0], primeiroDaFila[1]
        return True

    def decrementarCiclos(self):
        if(self.contadorRegressivo > 0 and self.emUso):
            self.contadorRegressivo -= 1

    def liberarDisco(self):
        # Libera o disco se o contador estiver em 0 se retorna True. Caso contrário retorna False

        if(not self.emUso) or (self.contadorRegressivo != 0):
            return False

        self.emUso = False
        self.jobUtilizandoODisco = None
        self.arquivoSendoAcessado = None
        return True

    def atualizar(self):
        # Returns do tipo [True/False, mensagem, tipo]
        # (True, 'Job * acessou o disco usando arquivo *', 'A') >> quando um job conseguir acesso ao disco
        # (True, 'Job * terminou de acessar o disco', 'F') >> Job terminou de acessar o disco
        # (False, None, None) >> quando não há alterações (nenhum job na fila e nenhum término de acesso)

        # Primeiro tento acessar o disco e, se houver sucesso, informo o fato que o houve um novo acesso ao disco
        if(self.acessarDisco()):
            return True, ('Job' + self.jobUtilizandoODisco + ' acessou disco para manipular o arquivo ' + self.arquivoSendoAcessado), 'A'

        # Depois verifico se o job corrente já terminou seu acesso ao disco
        jobQueUsavaODisco = self.jobUtilizandoODisco
        self.decrementarCiclos()
        if(self.liberarDisco()):
            return True, ('Job ' + jobQueUsavaODisco + ' terminou de acessar o disco'), 'F'

    def exibirEstado(self):
        if(self.emUso):
            print('Disco em uso pelo job ' + str(self.jobUtilizandoODisco) + ' acessando o arquivo ' + str(self.arquivoSendoAcessado))
            print('Ciclos remanescentes para encerrar o acesso: ' + str(self.contadorRegressivo))
        else:
            print('Disco não está em uso')

    def exibirArquivos(self):
        print('Arquivos presentes em disco:')
        for key in self.arquivos.keys():
            print('\r\nNome: ' + str(key))
            print('Tamanho: ' + str(self.arquivos[key][0]))
            print('Proprietário(s): ' + str(self.arquivos[key][1]))
