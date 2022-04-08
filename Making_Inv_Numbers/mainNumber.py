import os
import re


class MainSet:
    def __init__(self, setRange):
        self.theSet = {str(num) for num in range(setRange[0], setRange[1])}

    def checkSet(self, value):
        if value:
            return len(self.theSet) < value
        else:
            return len(self.theSet)
    
    def getElm(self):
        return self.theSet.pop()


class Data:
    def __init__(self, baseInput):
        self.baseNum = baseInput
        self.userInput = str()
        self.datalist = list()
        self.msgDict = {1: 'Не осталось свободных номеров. Работа программы будет завершена.',
                        2: 'Нет столько доступных номеров.',
                        3: 'Введена неправильная команда, поропбуйте снова',
                        4: 'Номеров записано: '}

        self.resFile = open('result.txt', 'w')
        self.resFile.close()
    
    def inputing(self, rest):
        os.system('cls')
        print('Свободных номеров осталось: %d' % rest)
        self.userInput = input('Введите "х:у" для получения Х номеров по У предметов в каждом (0 для выхода): ')

    def getMsg(self, msgMark):
        print(self.msgDict[msgMark])
        os.system('pause')

    def dataCheck(self, data):
        if re.fullmatch(r'\d{1,3}:\d{1,3}', data):
           self.datalist = list(map(int, data.split(':')))
        else:
            return True

    def fileWrite(self, inpList, setObj):
        self.resFile = open('result.txt', 'a')
        for _ in range(self.datalist[0]):
            resNum = self.baseNum
            for _ in range(int(self.datalist[1])):
                resNum = resNum + setObj.pop() + ';'
            resNum = resNum.rstrip(';')
            self.resFile.write(resNum + '\n')
        self.resFile.close()



if __name__ == '__main__':
    usrSet = MainSet([100, 300])
    usrData = Data(input('Введите базовый номер: '))

    while True:
        if not usrSet.checkSet(None):
            usrData.getMsg(1)
            exit(0)
        usrData.inputing(usrSet.checkSet(None))

        if usrData.userInput == '0':
            exit(0)

        if  usrData.dataCheck(usrData.userInput):
            usrData.getMsg(3)
            continue
        
        if usrSet.checkSet(usrData.datalist[0] * usrData.datalist[1]):
            usrData.getMsg(2)
            continue

        usrData.fileWrite(usrData.datalist, usrSet.theSet)
