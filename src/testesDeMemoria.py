from jobs import Job, Segmento, lerJobDoArquivo, montarTabelaDeJobs
from memoria import RAM


listaDeNomes = ['A.txt', 'B.txt', 'C.txt', 'D.txt', 'E.txt']
tabelaDeJobs = montarTabelaDeJobs(listaDeNomes=listaDeNomes)
# for job in tabelaDeJobs:
#     job.mostrarRequisitosDoJob()
#     job.mostrarArvore()

memoria = RAM(tamanho=2**16)
tabelaDeJobs[0].definirSegmentosAtivos([0, 1, 3])
tabelaDeJobs[1].definirSegmentosAtivos([0, 1, 4])
tabelaDeJobs[2].definirSegmentosAtivos([0, 1, 2, 4])
tabelaDeJobs[3].definirSegmentosAtivos([0, 2])
tabelaDeJobs[4].definirSegmentosAtivos([0, 2])

for job in tabelaDeJobs:
    memoria.alocarNovoJob(job)

memoria.alocarJobDaFila()
print('\r\nSegment map table após a inclusão do job A:')
memoria.mostrarSegmentTable()
print('Espaços ocupados após a inclusão do job A:')
memoria.mostrarEspacosOcupados()

print('\r\n>>>1<<<<')

memoria.alocarJobDaFila()
print('\r\nSegment map table após a inclusão dos job A e B')
memoria.mostrarSegmentTable()
print('Espaços ocupados após a inclusão dos jobs A e B:')
memoria.mostrarEspacosOcupados()

print('\r\n>>>2<<<<')

memoria.alocarJobDaFila()
print('\r\nSegment map table após a inclusão dos job A, B e C')
memoria.mostrarSegmentTable()
print('Espaços ocupados após a inclusão dos jobs A, B, C e D:')
memoria.mostrarEspacosOcupados()

print('\r\n>>>3<<<<')

memoria.alocarJobDaFila()
print('\r\nSegment map table após a inclusão dos job A, B, C e D')
memoria.mostrarSegmentTable()
print('Espaços ocupados após a inclusão dos jobs A, B, C e D:')
memoria.mostrarEspacosOcupados()

print('\r\n>>>4<<<<')
memoria.liberarJob('C')
print('\r\nSegment map table após a liberação do job C:')
memoria.mostrarSegmentTable()
print('Espaços ocupados após a liberação do job C:')
memoria.mostrarEspacosOcupados()

print('\r\n>>>5<<<<')
memoria.alocarNovoJob(tabelaDeJobs[4])
memoria.alocarJobDaFila()
print('\r\nSegment map table após a inclusão dos job A, B, D e E')
memoria.mostrarSegmentTable()
print('Espaços ocupados após a inclusão dos jobs A, B, D e E:')
memoria.mostrarEspacosOcupados()
