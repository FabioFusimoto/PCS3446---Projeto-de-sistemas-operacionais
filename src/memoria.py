class RAM:
    def __init__(self, tamanho):
        self.tamanho = tamanho
        # A segmentTable terá a forma ST[str(job) + str(segmento)] = [endInicial, tamanhoDoSegmento]
        self.segmentTable = {}
        self.fileTable = {}
        self.espacosOcupados = []
        self.fila = []

    def alocarJobDaFila(self):
        pass

    def alocarNovoJob(self, job):
        pass

    def liberarJob(self, nomeDoJob):
        pass

    def carregarArquivoDoDisco(nomeDoArquivo, jobSolicitante):
        pass

    def verificarPresencaDeSegmento(nome):
        pass
