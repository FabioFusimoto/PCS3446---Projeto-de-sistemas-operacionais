import texttable


class DeviceManager:
    def __init__(self, dispositivos):
        # dispositivos é um dict do tipo disp[nome] = tAcesso
        self.dispositivos = dispositivos

        # elementos da fila são do tipo [nome do dispositivo, job solicitante]
        # um acesso bloqueado ao E0 não deve impedir o acesso ao S1, por exemplo, se esse estiver livre
        self.fila = []

        # acessosCorrentes[nomeDoDispositivo] = [job solicitante, tempoRemanescente]
        self.acessosCorrentes = {}

    def solicitarES(self, nomeDoDispositivo, nomeDoJob):
        self.fila.append([nomeDoDispositivo, nomeDoJob])

    def acessarDispositivo(self, nomeDoDispositivo, nomeDoJob):
        # True significa que o dispositivo foi acessado com sucesso
        # False significa que o dispositivo não pôde ser acessado porque já estava ocupado
        if(nomeDoDispositivo not in self.acessosCorrentes.keys()):
            self.acessosCorrentes[nomeDoDispositivo] = [nomeDoJob, self.dispositivos[nomeDoDispositivo]]
            return True
        else:
            return False

    def finalizarAcesso(self, nomeDoDispositivo):
        if(nomeDoDispositivo in self.acessosCorrentes.keys()):
            if(self.acessosCorrentes[nomeDoDispositivo][1] == 0):
                jobQueUsavaODispositivo = self.acessosCorrentes[nomeDoDispositivo][0]
                del self.acessosCorrentes[nomeDoDispositivo]
                return True, jobQueUsavaODispositivo
        return False, None

    def atualizar(self):
        # O processo de atualização é um pouco diferente porque múltiplas ações podem ocorrer simultaneamente
        houveAtualizacao = False
        mensagem = ''
        jobsQueIniciaramES = []  # elementos da forma [nomeDoJob, nomeDoDispositivo]
        jobsQueFinalizaramES = []  # elementos da forma [nomeDoJob, nomeDoDispositivo]

        # Primeiro decremento t de todos os acessos correntes verifico quais foram finalizados
        for key in self.acessosCorrentes.keys():
            self.acessosCorrentes[key][1] -= 1

        for disp in self.dispositivos.keys():
            acessoFinalizado, jobQueUsavaODispositivo = self.finalizarAcesso(nomeDoDispositivo=disp)
            if(acessoFinalizado):
                houveAtualizacao = True
                mensagem += ' Dispositivo ' + disp + ' finalizou o processo de E/S.'
                jobsQueFinalizaramES.append([jobQueUsavaODispositivo, disp])

        # Em seguida tento alocar os acessos da fila
        solicitacoesComSucesso = []
        for i in range(len(self.fila)):
            nomeDoDispositivo = self.fila[i][0]
            jobQueVaiUsarODispositivo = self.fila[i][1]
            if(self.acessarDispositivo(nomeDoDispositivo=nomeDoDispositivo, nomeDoJob=jobQueVaiUsarODispositivo)):
                houveAtualizacao = True
                mensagem += ' Job ' + self.fila[i][1] + ' iniciou o acesso ao dispositivo ' + self.fila[i][0] + '.'
                solicitacoesComSucesso.append([self.fila[i][0], self.fila[i][1]])
                jobsQueIniciaramES = [jobQueUsavaODispositivo, nomeDoDispositivo]
        for s in solicitacoesComSucesso:
            index = self.fila.index(s)
            del self.fila[index]

        return houveAtualizacao, mensagem, jobsQueIniciaramES, jobsQueFinalizaramES

    def mostrarEstado(self):
        t = texttable.Texttable()
        linhas = []
        linhas.append(['Nome', 'Sendo acessado', 'Job', 'Tempo remanescente'])
        for nomeDoDispositivo in self.dispositivos.keys():
            linha = []
            linha.append(nomeDoDispositivo)
            if(nomeDoDispositivo not in self.acessosCorrentes.keys()):
                linha.append('Não')
                linha.append('-')
                linha.append('-')
            else:
                linha.append('Sim')
                linha.append(self.acessosCorrentes[nomeDoDispositivo][0])
                linha.append(self.acessosCorrentes[nomeDoDispositivo][1])
            linhas.append(linha)
        t.add_rows(linhas)
        print('\r\nEstado do gerenciador de dispositivos\r\n')
        print(t.draw())

        t = texttable.Texttable()
        linhas = []
        linhas.append(['Dispositivo a acessar', 'Job solicitante'])
        for elemento in self.fila:
            linha = [elemento[0], elemento[1]]
            linhas.append(linha)
        t.add_rows(linhas)
        print('\r\nFila de espera do gerenciador de dispositivos')
        print(t.draw())
