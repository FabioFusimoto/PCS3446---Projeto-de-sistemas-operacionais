from jobs import Job, Segmento, lerJobDoArquivo, montarTabelaDeJobs


listaDeNomes = ['A.txt', 'B.txt', 'C.txt']
tabelaDeJobs = montarTabelaDeJobs(listaDeNomes=listaDeNomes)
tabelaDeJobs[0].definirSegmentosAtivos([0, 1, 3])
tabelaDeJobs[1].definirSegmentosAtivos([0, 2, 6])
tabelaDeJobs[2].definirSegmentosAtivos([0, 1, 3, 5, 7])
for job in tabelaDeJobs:
    job.mostrarRequisitosDoJob()
    job.mostrarArvore()
