from simulador import SIM
import os.path


# ----- ARGUMENTOS DE SIMULAÇÃO -----

# Duração da simulação. Deve ser um número inteiros e maior que zero
duracaoSimulacao = 10000

# Número máximo de jobs a se alocar para o processador ao mesmo tempo, deve ser maior que zero
numMaximoDeJobs = 2

# Lista de jobs a serem executados. Deve conter a extensão .txt
# Os jobs estão descritos no diretório /txt/jobs
listaDeJobs = ['A.txt', 'B.txt', 'C.txt']

# Instantes em que os jobs são submetidos (deve ter o mesmo tamanho que a lista de jobs)
instantesDeSubmissao = [0, 0, 50]

# Tamanho da memória em bytes
tamanhoDaMemoria = 2**16

# Tamanho do disco em bytes
tamanhoDoDisco = 2**20

# Tempo (em t) que leva para acessar o disco
tAcessoAoDisco = 50

# Arquivos a serem acessados
# Os nomes válidos estão explicitados no arquivo /txt/files/arquivos.txt
nomeDosArquivos = ['file1', 'file2']

# Time slice do processador até que ocorra uma mudança do job corrente
timeSliceProcessador = 25

# Tempos de acesso dos dispositivos E0, E1, S0 e S1, respectivamente. Devem ser inteiros maiores que 0
tAcessoDosDispositivos = [10, 20, 35, 18]

# Eventos que se deseja rastrear
triggersEvento = ['JNIF', 'FJ', 'AID']

# Instantes em que se deseja observar o estado da simulação
triggersTempo = [2500, 1800]

# ----- TÉRMINO DOS ARGUMENTOS, INÍCIO DA SIMULAÇÃO -----
dispositivos = {}
dispositivos['E0'] = tAcessoDosDispositivos[0]
dispositivos['E1'] = tAcessoDosDispositivos[1]
dispositivos['S0'] = tAcessoDosDispositivos[2]
dispositivos['S1'] = tAcessoDosDispositivos[3]

simulador = SIM(duracaoSimulacao=duracaoSimulacao, numMaximoDeJobs=numMaximoDeJobs, listaDeJobs=listaDeJobs,
                instantesDeSubmissao=instantesDeSubmissao, tamanhoDaMemoria=tamanhoDaMemoria, tamanhoDoDisco=tamanhoDoDisco,
                tAcessoAoDisco=tAcessoAoDisco, nomeDosArquivos=nomeDosArquivos, timeSliceProcessador=timeSliceProcessador,
                dispositivos=dispositivos)

continuarSimulacao = True
while(continuarSimulacao):
    continuarSimulacao, eventos = simulador.avancarSimulacao()
    mostrarEstado = False
    for ev in eventos:
        if ev in triggersEvento:
            print('\r\nCiclo ' + str(simulador.instanteAtual) + ': ocorrência do evento do tipo ' + ev)
            mostrarEstado = True
            break
    if (not mostrarEstado) and (simulador.instanteAtual in triggersTempo):
        print('\r\nCiclo ' + str(simulador.instanteAtual))
        mostrarEstado = True
    if mostrarEstado:
        simulador.mostrarEstado()

simulador.inserirLogNoArquivo(nomeDoArquivo='log.txt')
print('Log gerado e copiado no arquivo ' + str(os.path.split(os.path.dirname(__file__))[0]) + '/log.txt')
