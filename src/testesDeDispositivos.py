from dispositivos import DeviceManager


print('\r\n-----INICIALIZANDO OS DISPOSITIVOS----')
dispositivos = {}
dispositivos['E0'] = 10
dispositivos['E1'] = 20
dispositivos['S0'] = 35
dispositivos['S1'] = 18
GD = DeviceManager(dispositivos=dispositivos)
GD.mostrarEstado()

print('\r\n-----INSERINDO SOLICITAÇÕES DE ACESSO A E0 E S0, ATUALIZANDO E VERIFICANDO O ESTADO APÓS ATUALIZAÇÃO----')
GD.solicitarES('E0', 'A')
GD.solicitarES('S0', 'C')
houveAtualizacao, mensagem = GD.atualizar()
if(houveAtualizacao):
    print(mensagem)
GD.mostrarEstado()

print('\r\n-----ATUALIZANDO POR VÁRIOS CICLOS E VERIFICANDO MUDANÇAS E O ESTADO DOS DISPOSITIVOS APÓS AS MUDANÇAS----')
for i in range(1, 200):
    houveAtualizacao, mensagem = GD.atualizar()
    if(houveAtualizacao):
        print('\r\n=====Ciclo #' + str(i) + '=====')
        print(mensagem)
        GD.mostrarEstado()
    if(i == 5):
        # No ciclo 6, chega um novo job que deseja acessar E0, mas não pode pois A está acessando atualmente
        GD.solicitarES('E0', 'D')
    if(i == 12):
        # No ciclo 13, chega um novo job que deseja acessar E0, mas não pode pois A está acessando atualmente
        GD.solicitarES('E0', 'F')
    if(i == 14):
        # No ciclo 15 surge uma solicitação de acesso ao S1
        GD.solicitarES('S1', 'B')
    if(i == 80):
        # No ciclo 81 surge uma solicitação de acesso ao E1
        GD.solicitarES('E1', 'E')
