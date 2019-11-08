import os.path
import texttable


class HD:
    def __init__(self, tamanho, numCiclos, listaDeNomes):
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

        # Guarda a posiçao do último arquivo que foi inserido no disco
        self.ultimoEspacoOcupado = 0

        # Fila com o nome dos jobs que desejam acessar arquivos do disco. O job na última posição da fila tem maior prioridade
        # Constituído de elementos do tipo [nomeDoJob, nomeDoArquivo]
        self.fila = []

        # arquivos[nome] = [tamanho, [lista de jobs que podem acessar o arquivo]] - a lista de jobs pode incluir 'Public' indicando que é acessível a todos os jobs
        self.arquivos = {}
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

    def validarAcesso(self, nomeDoJob, nomeDoArquivo):
        # Retorna True se o acesso for permitido e False caso contrário. Retorna também uma mensagem de erro
        # Arquivo inexistente
        if nomeDoArquivo not in self.arquivos.keys():
            return False, ('O arquivo ' + nomeDoArquivo + ' não existe')

        # Acesso proibido
        if ('Public' not in self.arquivos[nomeDoArquivo][1]) and (nomeDoJob not in self.arquivos[nomeDoArquivo][1]):
            return False, ('O job ' + nomeDoJob + ' não tem acesso ao arquivo ' + nomeDoArquivo)

        return True, ('Job ' + nomeDoJob + ' solicitou acesso ao arquivo ' + nomeDoArquivo)

    def solicitarAcessoAoDisco(self, nomeDoJob, nomeDoArquivo):
        # Verifica-se se dado job tem acesso ao arquivo
        # Retorna-se True se a solicitação for válida e True caso contrário
        # Retorna uma mensagem de erro caso o primeiro valor seja 'False'

        acessoValido, mensagem = self.validarAcesso(nomeDoJob=nomeDoJob, nomeDoArquivo=nomeDoArquivo)
        if(acessoValido):
            # Acesso permitido, insere-se a solicitação de acesso na fila
            self.fila.insert(0, [nomeDoJob, nomeDoArquivo])

        return acessoValido, mensagem

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
        # (True, nome do job que iniciou acessou o disco,'Job * acessou o disco usando arquivo *', 'A', nome do arquivo sendo acessado) >> quando um job conseguir acesso ao disco
        # (True, nome do job que finalizou o acesso ao disco,'Job * terminou de acessar o disco', 'F', nome do arquivo que terminou de ser acessado) >> Job terminou de acessar o disco
        # (False, nome do job acessando o disco, None, None, nome do arquivo atualmente acessado) >> quando não há alterações (nenhum job na fila e nenhum término de acesso)

        # Primeiro tento acessar o disco e, se houver sucesso, informo o fato que o houve um novo acesso ao disco
        if(self.acessarDisco()):
            return True, self.jobUtilizandoODisco, ('Job ' + self.jobUtilizandoODisco + ' iniciou o acesso ao arquivo ' + self.arquivoSendoAcessado), 'A', self.arquivoSendoAcessado

        # Depois verifico se o job corrente já terminou seu acesso ao disco
        jobQueUsavaODisco = self.jobUtilizandoODisco
        arquivoQueOJobAcessou = self.arquivoSendoAcessado
        self.decrementarCiclos()
        if(self.liberarDisco()):
            return True, jobQueUsavaODisco, ('Job ' + jobQueUsavaODisco + ' terminou de acessar o disco e trouxe o arquivo ' + arquivoQueOJobAcessou + ' para a memória'), 'F', arquivoQueOJobAcessou

        # Nenhuma mudança ocorreu
        return False, self.jobUtilizandoODisco, None, None, self.arquivoSendoAcessado

    def exibirEstado(self):
        if(self.emUso):
            print('Disco em uso pelo job ' + str(self.jobUtilizandoODisco) + ' acessando o arquivo ' + str(self.arquivoSendoAcessado))
            print('Ciclos remanescentes para encerrar o acesso: ' + str(self.contadorRegressivo))
        else:
            print('Disco não está em uso')

    def exibirArquivos(self):
        print('Arquivos presentes em disco:')
        t = texttable.Texttable()
        t.add_row(['Nome do arquivo', 'Tamanho', 'Donos'])
        for key in self.arquivos.keys():
            t.add_row([key, self.arquivos[key][0], self.arquivos[key][1]])
        print(t.draw())
