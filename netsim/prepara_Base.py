import datetime


class prepara_arquivos:

    def __init__(self, arqplan, arqexec):
        self.arqplan = arqplan
        self.arqexec = arqexec

    def montaPlanejados(self, arqSAIDA):
        rotDICT = self.dict_rot(1)
        with open(arqSAIDA, 'w') as wr:
            with open(self.arqplan, 'r') as f:
                line = f.readline()
                while line:
                    fields = line.split(';')
                    if fields[0].lower().strip() != 'date':
                        dtvoo = datetime.datetime.strptime(fields[0], '%d/%b/%Y').date().strftime('%Y%m%d')
                        voo = "G3 " + fields[3] + " "
                        orig = fields[4]
                        dest = fields[7]
                        hrSTD = fields[5].split(':')
                        if hrSTD[0] == '24':
                            std = '00' + hrSTD[1]
                        else:
                            std = hrSTD[0] + hrSTD[1]
                        hrSTA = fields[6].split(':')
                        if hrSTA[0] == '24':
                            sta = '00' + hrSTA[1]
                        else:
                            sta = hrSTA[0] + hrSTA[1]
                        cfgeqt = fields[1].split("/")
                        if cfgeqt[1] == "73G":
                            teqt = "B73G"
                        else:
                            teqt = "B738"
                        eqt = cfgeqt[1]
                        achaROT = cfgeqt[1] + ' ' + fields[2]
                        rot = str(rotDICT[achaROT]) # fields[2]
                        _lntxtGrava = "PLEG|" + dtvoo + "|" + voo + "|" + orig + "|" + dest + "|" + dtvoo + "|" + std + "|" + sta + "|" + \
                                      dtvoo + "|" + std + "|" + sta + "|" + teqt + "|" + eqt + "|G3|G3" + '\n' + "POPT|" + rot + "|\n"
                        wr.write(_lntxtGrava)
                    line = f.readline()

    def montaExecutados(self, arqSAIDA):
        rotDICT = self.dict_rot(2)
        with open(arqSAIDA, 'w') as wr:
            with open(self.arqexec, 'r') as f:
                line = f.readline()
                while line:
                    fields = line.split(';')
                    if (fields[0].isdigit()) and (fields[1].upper() == "ARR"):
                        #if fields[0].lower().strip() != 'date':
                        dtvoo = datetime.datetime.strptime(fields[11], '%d/%m/%Y').date().strftime('%Y%m%d')
                        voo = "G3 " + fields[0] + " "
                        orig = fields[7]
                        dest = fields[8]
                        hrSTD = fields[12].split(':')
                        if hrSTD[0] == '24':
                            std = '00' + hrSTD[1]
                        else:
                            std = hrSTD[0] + hrSTD[1]
                        hrSTA = fields[21].split(':')
                        if hrSTA[0] == '24':
                            sta = '00' + hrSTA[1]
                        else:
                            sta = hrSTA[0] + hrSTA[1]
                        #cfgeqt = fields[1].split("/")
                        if fields[28] == "73G":
                            teqt = "B73G"
                        else:
                            teqt = "B738"
                        eqt = fields[28]
                        rot = str(rotDICT[fields[29]])
                        _lntxtGrava = "PLEG|" + dtvoo + "|" + voo + "|" + orig + "|" + dest + "|" + dtvoo + "|" + std + "|" + sta + "|" + \
                                      dtvoo + "|" + std + "|" + sta + "|" + teqt + "|" + eqt + "|G3|G3"
                        wr.write(_lntxtGrava)
                        wr.write('\n')
                        wr.write("POPT|" + rot + "|")
                        wr.write('\n')
                    line = f.readline()

    def dict_rot(self, idarq):
        if idarq == 1:
            with open(self.arqplan, 'r') as f:
                idRot = 1
                dictROT = {}
                line = f.readline()
                while line:
                    fields = line.split(';')
                    if (fields[0].lower() != 'date'):
                        cfgeqt = fields[1].split("/")
                        rotmod = cfgeqt[1] + ' ' + fields[2]
                        if (not rotmod in dictROT.keys()):
                            dictROT[rotmod] = idRot
                            idRot += 1
                    line = f.readline()
        else:
            with open(self.arqexec, 'r') as f:
                idRot = 1
                dictROT = {}
                line = f.readline()
                while line:
                    fields = line.split(';')
                    if (fields[0].isdigit()) and (not fields[29] in dictROT.keys()):
                        dictROT[fields[29]] = idRot
                        idRot += 1
                    line = f.readline()
        return dictROT
