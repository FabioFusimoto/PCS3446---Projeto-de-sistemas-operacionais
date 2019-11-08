from jobs import Job, Segmento, lerJobDoArquivo, montarTabelaDeJobs
from processador import CPU
import texttable


processador = CPU(timeSlice=50)

listaDeNomes = ['A.txt', 'B.txt', 'C.txt']
tabelaDeJobs = montarTabelaDeJobs(listaDeNomes=listaDeNomes)
tabelaDeJobs[0].definirSegmentosAtivos([0, 1, 3])
tabelaDeJobs[1].definirSegmentosAtivos([0, 2, 6])
tabelaDeJobs[2].definirSegmentosAtivos([0, 1, 2, 4])

print('\r\n1)-----INSERINDO JOBS NA FILA-----')
instantesE_S = [[25], [400], []]
for i in range(len(instantesE_S)):
    processador.adicionarNovoJob(job=tabelaDeJobs[i], instantesE_S=instantesE_S[i])

processador.mostrarFila()

print('\r\n2)-----ATUALIZANDO O PROCESSAMENTO 5 VEZES (EQUIVALENTE A ESPERAR 5 CICLOS)-----')
ciclo = 0
while(ciclo < 5):
    houveAtualizacao, mensagem, tipo, jobEnvolvido = processador.atualizar()
    print('\r\nCiclo #' + str(ciclo))
    if(houveAtualizacao):
        print(mensagem)
    else:
        print('Não houve atualizações')
    ciclo += 1

print('\r\n3)-----APÓS EXECUTAR 5 CICLOS-----')
processador.mostrarEstadoAtual()
processador.mostrarFila()

print('\r\n4)-----EXECUTANDO POR 10000 CICLOS E MOSTRANDO AS MUDANÇAS----')
tabelaDeAtualizacoes = texttable.Texttable()
tabelaDeAtualizacoes.add_row(['Instante', 'Atulização'])
while(ciclo < 10000):
    houveAtualizacao, mensagem, tipo, jobEnvolvido = processador.atualizar()
    if(houveAtualizacao):
        tabelaDeAtualizacoes.add_row([ciclo, mensagem])
    if(ciclo == 3000):
        processador.alternarParaModoPronto('B')
    if(ciclo == 5000):
        processador.alternarParaModoPronto('A')
    ciclo += 1
print(tabelaDeAtualizacoes.draw())
