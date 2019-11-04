from jobs import Job, Segmento, lerJobDoArquivo, montarTabelaDeJobs


listaDeNomes = ['A.txt', 'B.txt', 'C.txt']
tabelaDeJobs = montarTabelaDeJobs(listaDeNomes=listaDeNomes)
for job in tabelaDeJobs:
    job.mostrarRequisitosDoJob()
    job.mostrarArvore()
