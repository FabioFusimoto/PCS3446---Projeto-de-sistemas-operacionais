class HD:
    def __init__(self, tamanho, numCiclos):
        self.emUso = False
        self.numCiclos = numCiclos

        # arquivos[nome] = [tamanho, [lista de jobs que podem acessar o arquivo]] - a lista de jobs pode incluir 'Public' indicando que é acessível a todos os jobs
        self.arquivos = {}
        self.espacosOcupados = []
        self.contadorRegressivo = 0
        self.fila = []

    def adicionarArquivo(nome, tamanho):
        pass

    def acessoAoDisco(arquivo):
        pass

    def decrementarCiclos():
        pass
