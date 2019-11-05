from jobs import Job, Segmento, lerJobDoArquivo, montarTabelaDeJobs
from processador import CPU


processador = CPU(timeSlice=50)

listaDeNomes = ['A.txt', 'B.txt', 'C.txt']
tabelaDeJobs = montarTabelaDeJobs(listaDeNomes=listaDeNomes)
tabelaDeJobs[0].definirSegmentosAtivos([0, 1, 3])
tabelaDeJobs[1].definirSegmentosAtivos([0, 2])
tabelaDeJobs[2].definirSegmentosAtivos([0, 1, 3])

print('\r\n-----INSERINDO JOBS NA FILA-----')
instantesE_S = [[25, 252, 345], [400], []]
for i in range(len(instantesE_S)):
    processador.adicionarNovoJob(job=tabelaDeJobs[i], instantesE_S=instantesE_S[i])

processador.mostrarFila()

print('\r\n-----ATUALIZANDO O PROCESSAMENTO 5 VEZES (EQUIVALENTE A ESPERAR 5 CICLOS)')
ciclo = 0
while(ciclo < 5):
    houveAtualizacao, mensagem, tipo = processador.atualizar()
    print('\r\nCiclo #' + str(ciclo))
    if(houveAtualizacao):
        print(mensagem)
    else:
        print('Não houve atualizações')
    ciclo += 1

print('\r\n-----ESTADO DO PROCESSADOR APÓS EXECUTAR 5 CICLOS-----')
processador.mostrarEstadoAtual()
print('\r\n-----FILA DO PROCESSADOR APÓS EXECUTAR 5 CICLOS-----')
processador.mostrarFila()

print('\r\n-----EXECUTANDO E MOSTRANDO AS MUDANÇAS----')
while(ciclo < 10000):
    houveAtualizacao, mensagem, tipo = processador.atualizar()
    if(houveAtualizacao):
        print('\r\nResultados do ciclo #' + str(ciclo))
        print(mensagem)
    if(ciclo == 1500):
        print('\r\nResultados do ciclo #' + str(ciclo))
        processador.alternarParaModoPronto(nomeJob='A')
        print('Job A finalizou sua operação de E/S')
    if(ciclo == 2225):
        print('\r\nResultados do ciclo #' + str(ciclo))
        processador.alternarParaModoPronto(nomeJob='A')
        print('Job A finalizou sua operação de E/S')
    if(ciclo == 3200):
        print('\r\nResultados do ciclo #' + str(ciclo))
        processador.alternarParaModoPronto(nomeJob='B')
        print('Job B finalizou sua operação de E/S')
    if(ciclo == 4000):
        print('\r\nResultados do ciclo #' + str(ciclo))
        processador.alternarParaModoPronto(nomeJob='A')
        print('Job A finalizou sua operação de E/S')
    ciclo += 1
