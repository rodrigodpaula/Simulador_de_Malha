import sys
import random
import calendar

from datetime import datetime
from netsim.netline_parser import NetLineParser
from netsim.stat import *
from netsim.simulator import Simulator
from netsim.prepara_Base import prepara_arquivos

if __name__ == "__main__":
    if len(sys.argv) < 4:
        #        print 'Uso: python NetworkSim <pairings.txt> <block_folder> <begin:yyyymmdd> <end:yyyymmdd>'
        print 'Uso: python NetworkSim <arquivo:Mes> <semestre:1|2> <ref:yyyymm>'
        exit(0)

    random.seed()
    arqCSV = sys.argv[1]

    # Pesquisar pastas de input para localizar arquivos
    # pasta default = pasta do arquivo main.
    _pstDefault = os.getcwd()
    pastaDEF_PLAN = _pstDefault + '\input\planejados'
    lstDIR = os.listdir(pastaDEF_PLAN)
    _CSV_planejado = ""
    for arqPlan in lstDIR:
        arqtmp = arqPlan.split('-')
        if arqCSV.upper() == arqtmp[0].upper():
            _CSV_planejado = pastaDEF_PLAN + '\\' + arqPlan
            break
    if _CSV_planejado == "":
        print('Arquivo Planejado Nao localizado !')
        sys.exit(sys.exc_info())

    pastaDEF_EXEC = _pstDefault + '\input\executados'
    _CSV_executado = ""
    for arqExec in lstDIR:
        arqEtmp = arqExec.split('-')
        if arqCSV.upper() == arqEtmp[0].upper():
            _CSV_executado = pastaDEF_EXEC + '\\' + arqExec
            break
    if _CSV_executado == "":
        print('Arquivo Executado Nao localizado !')
        # sys.exit(sys.exc_info())

    # preparar os arquivos csv (Planejados e Executados) e gerar os arquivos txt de input
    # arqPlanejado = prepara_arquivos(_CSV_planejado, _CSV_executado)
    file_planejado = _CSV_planejado  # pastaDEF_PLAN + '\\' + arqCSV + '.csv'
    file_executado = _CSV_executado  # pastaDEF_EXEC + '\\' + arqCSV + '.txt'
    #    try:
    #        arqPlanejado.montaPlanejados(file_planejado)
    #    except:
    #        print('Erro ao processar o arquivo planejado\n Verifique o arquivo e execute a operacao novamente')
    #        sys.exit(sys.exc_info())
    #    try:
    #        arqPlanejado.montaExecutados(file_executado)
    #    except:
    #        print('Erro ao processar o arquivo executado\n Verifique o arquivo e execute a operacao novamente')
    #        sys.exit(sys.exc_info())

    # repticao para processar planejado e executado
    _conta_proc = 0
    while _conta_proc < 1:
        if (_conta_proc == 0):
            procAtual = 'Planejados'
            file_name = file_planejado
            arqFinal = 'legs_Planejados.csv'
        else:
            procAtual = 'Executados'
        #            file_name = file_executado
        #            arqFinal = 'legs_Executados.csv'

        print ('Processando dados ' + procAtual + '\n')

        # file_name = sys.argv[1]
        print 'Processando malha. Arquivo: %s...' % file_name
        parser = NetLineParser(file_name)
        parser.parse()
        print 'Airports = %d' % len(parser.network.airports)
        print 'Fleets   = %d' % len(parser.network.fleets)
        print 'Legs     = %d' % len(parser.network.legs)
        print 'Routes   = %d' % len(parser.network.routes)
        # parser.network.print_crew_flow()

        if int(sys.argv[2]) == 1:
            data_folder = _pstDefault + '\\input\\block\\2016_01_11\\'
        else:
            data_folder = _pstDefault + '\\input\\block\\2016_06_11\\'

        print 'Processando dados. Pasta: %s...' % data_folder

        data_folder = data_folder.replace('\\', '/')
        btgen = Percentile(data_folder, 50)
        # btgen = Kernel(data_folder)
        btgen.init()
        # begin = datetime.strptime('%s 0000' % '20170901', '%Y%m%d %H%M')
        # end = datetime.strptime('%s 2359' % '20170930', '%Y%m%d %H%M')
        periodoREF = sys.argv[3]
        anoREF = int(periodoREF[0:4])
        mesREF = int(periodoREF[4:])
        fimMes = calendar.monthrange(anoREF, mesREF)
        iniper = periodoREF + '01'
        fimper = periodoREF + str(fimMes[1])
        begin = datetime.strptime('%s 0000' % iniper, '%Y%m%d %H%M')
        end = datetime.strptime('%s 2359' % fimper, '%Y%m%d %H%M')

        print 'Simulando...'
        netsim = Simulator(parser.network, btgen)
        netsim.simulate(begin, end)
        netsim.output(arqFinal)
        _conta_proc += 1
