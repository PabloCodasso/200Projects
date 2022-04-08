import zipfile
import xml.etree.ElementTree as Et
from pathlib import Path
from time import sleep


class Parser:
    def __init__(self):
        self.lnList = list()
        self.innList = list()
        self.snilsList = list()
        self.nameList = list()
        self.fileList = list()
        self.guidlist = list()

    def parseXML(self):
        for zipName in Path(r'\\192.168.0.137\black\200\Команды контрактников\210. 03667 от 21.02.22').glob('*.zip'):
            archive = zipfile.ZipFile(zipName, 'r')
            xmlFile = archive.read('data.xml')
            xmlRoot = Et.fromstring(xmlFile)
            sleep(0.2)
