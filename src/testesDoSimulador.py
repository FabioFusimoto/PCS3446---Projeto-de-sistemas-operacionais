from simulador import SIM
import os.path


dispositivos = {}
dispositivos['E0'] = 10
dispositivos['E1'] = 20
dispositivos['S0'] = 35
dispositivos['S1'] = 18
print('\r\n1)-----INICIALIZANDO E VERIFICANDO A RANDOMIZAÇÃO DOS SEGMENTOS-----')
simulador = SIM(duracaoSimulacao=10000, numMaximoDeJobs=2, listaDeJobs=['A.txt', 'B.txt', 'C.txt'],
                instantesDeSubmissao=[0, 0, 50], tamanhoDaMemoria=2**16, tamanhoDoDisco=2**20,
                tAcessoAoDisco=50, nomeDosArquivos=['file1', 'file2'], timeSliceProcessador=25,
                dispositivos=dispositivos)
for j in simulador.jobs:
    print('\r\nSegmentos ativos do job ' + j.nome)
    print(j.segmentosAtivos)

print('\r\n2)-----INSTANTES DE INTERRUPÇÃO-----')
simulador.mostrarInstantesDeInterrupcao()

print('\r\n3)-----ADICIONANDO OS JOBS NA SIMULAÇÃO E VERIFICANDO O LOG-----')
simulador.avancarSimulacao()
simulador.mostrarLog()

print('\r\n-----RESULTADO DA SIMULAÇÃO ATÉ SEU TÉRMINO-----')
print('Os resultados serão escritos no arquivo log.txt no diretório ' + str(os.path.split(os.path.dirname(__file__))[0]))
avancarSimulacao = True
while(avancarSimulacao):
    avancarSimulacao, eventos = simulador.avancarSimulacao()
    pass
simulador.inserirLogNoArquivo(nomeDoArquivo='log.txt')
