from pathlib import Path
# from Engine import analisys as anal
from threading import Thread
from itertools import cycle
import time
from multiprocessing import Pipe


def getHomeDir():  # Просмотр домашней папки
    print("This is home dir: " + str(Path.home()))


def testDIR():
    tstObj = anal.Parser()
    tstObj.parseXML()


def testThread():
    print('Function start')
    time.sleep(10)
    print('Function end')


def testPrcs():
    print("Point Zero")
    time.sleep(3)
    print("Middle point")
    time.sleep(3)
    print("Finish point")

def mayn():  # Печать в консоль Processing... с анимированными точками (типа процесс идёт)
    parsThread = Thread(target=testDIR)
    parsThread.start()
    it = cycle(['.'] * 3 + ['\b \b'] * 3)  # 
    print('Searching', end='')
    while parsThread.is_alive():
        time.sleep(1)
        print(next(it), end='', flush=True)

def pipes_test():
    par, chl = Pipe()
    if par.poll():
        print(par.recv())
    chl.send('1')
    print(par.recv())


if __name__ == "__main__":
    pipes_test()
