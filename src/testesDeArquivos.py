from disco import HD
from memoria import RAM
from jobs import Job, Segmento, lerJobDoArquivo, montarTabelaDeJobs

print('\r\n-----INICIALIZANDO E VERIFICANDO O ESTADO E OS ARQUIVOS-----')
arquivosACarregar = ['file1', 'file2', 'file4']
disco = HD(tamanho=2**20, numCiclos=5, listaDeNomes=arquivosACarregar)
memoria = RAM(tamanho=2**10)

disco.exibirEstado()
disco.exibirArquivos()

print('\r\n-----REALIZANDO UMA SOLICITAÇÃO E ACESSO VÁLIDOS-----')
solicitadoComSucesso, mensagem = disco.solicitarAcessoAoDisco(nomeDoJob='A', nomeDoArquivo='file1')
print(mensagem)

acesso = disco.acessarDisco()
if(acesso):
    print('Acesso ao disco realizado com sucesso')
else:
    print('O disco não pôde ser acessado')

print('\r\n-----DECREMENTANDO UM CICLO E VERIFICANDO O ESTADO QUANDO HÁ UM ACESSO CORRENTE-----')
disco.decrementarCiclos()
disco.exibirEstado()

print('\r\n-----ACESSANDO O DISCO ENQUANTO HÁ UMA OPERAÇÃO CORRENTE-----')
acesso = disco.acessarDisco()
if(acesso):
    print('Acesso ao disco realizado com sucesso')
else:
    print('O disco não pôde ser acessado')
disco.exibirEstado()

print('\r\n-----TENTANDO LIBERAR O DISCO ENQUANTO HÁ UMA OPERAÇÃO CORRENTE-----')
liberar = disco.liberarDisco()
if(liberar):
    print('Disco liberado com sucesso')
else:
    print('Disco não pôde ser liberado')

print('\r\n-----FINALIZANDO O ACESSO E LIBERANDO O DISCO-----')
disco.decrementarCiclos()
disco.decrementarCiclos()
disco.decrementarCiclos()
disco.decrementarCiclos()
liberar = disco.liberarDisco()
if(liberar):
    print('Disco liberado com sucesso')
else:
    print('Disco não pôde ser liberado')
disco.exibirEstado()

print('\r\n-----REALIZANDO UMA SOLICITAÇÃO DE ACESSO INVÁLIDA-----')
solicitadoComSucesso = disco.solicitarAcessoAoDisco(nomeDoJob='A', nomeDoArquivo='file4')
if(solicitadoComSucesso):
    print('Job A acessou o arquivo file4 com sucesso')
else:
    print('Job A não pôde acessar o arquivo file4')

print('\r\n-----INSERINDO UM ARQUIVO DO DISCO PARA A MEMÓRIA, COM SUCESSO-----')
inserir = memoria.carregarArquivoDoDisco(nomeDoArquivo='file1', jobSolicitante='A', disco=disco)
if(inserir):
    print('O arquivo file1 foi carregado em memória, conforme solicitação do Job A')
else:
    print('O arquivo file1 não foi carregado em memória mediante solicitação do Job A')
memoria.mostrarFileTable()

print('\r\n-----DECLARANDO QUE UM OUTRO JOB TAMBÉM DEPENDE DO ARQUIVO file1-----')
inserir = memoria.carregarArquivoDoDisco(nomeDoArquivo='file1', jobSolicitante='B', disco=disco)
memoria.mostrarFileTable()

print('\r\n-----REMOVENDO O JOB A DA MEMÓRIA E VERIFICANDO QUE O file1 PERMANECE NA MEMÓRIA, PORQUE O B TAMBÉM DEPENDE DELE-----')
listaDeNomes = ['A.txt', 'B.txt']
tabelaDeJobs = montarTabelaDeJobs(listaDeNomes=listaDeNomes)
tabelaDeJobs[0].definirSegmentosAtivos([0, 1, 3])
tabelaDeJobs[1].definirSegmentosAtivos([0, 2])
memoria.alocarNovoJob(tabelaDeJobs[0])
memoria.alocarJobDaFila()
memoria.alocarNovoJob(tabelaDeJobs[1])
memoria.alocarJobDaFila()
memoria.liberarJob('A')
memoria.mostrarFileTable()

print('\r\n-----REMOVENDO O JOB B DA MEMÓRIA E VERIFICANDO QUE O file1 FOI REMOVIDO DA MEMÓRIA, POIS MAIS NENHUM JOB DEPENDE DELE-----')
memoria.liberarJob('B')
memoria.mostrarSegmentTable()
memoria.mostrarFileTable()
