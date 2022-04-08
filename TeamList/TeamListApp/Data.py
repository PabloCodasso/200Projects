import Datetime

# Класс описания объекта команды.
class Team:
    def __init__(self, teamId, values = {}):
        self.id = teamId

        self.setComSpgmId(values.get('comSpgmId', ''))
        self.setComFormId(values.get('comFormId', ''))
        self.setOutDate(values.get('outDate', ''))
        self.setStation(values.get('station', ''))
        self.setMilType(values.get('milType', ''))
        self.setMilUnitName(values.get('milUnitName', ''))
        self.setSerialNumber(values.get('serialNumber'))
        self.setPeople(values.get('people', {}))
        self.setTreeItem(None)

    def __eq__(self, other):
        return (
            self.getId() == other.getId()
            and self.getComSpgmId() == other.getComSpgmId()
            and self.getComFormId() == other.getComFormId()
            and self.getOutDate() == other.getOutDate()
            and self.getStation() == other.getStation()
            and self.getMilType() == other.getMilType()
            and self.getMilUnitName() == other.getMilUnitName()
        )

    def setComSpgmId(self, comSpgmId):
        self.comSpgmId = comSpgmId

    def setComFormId(self, comFormId):
        self.comFormId = comFormId

    def setOutDate(self, outDate):
        self.outDate = outDate

    def setStation(self, station):
        self.station = station

    def setMilType(self, milType):
        self.milType = milType

    def setMilUnitName(self, milUnitName):
        self.milUnitName = milUnitName

    def setSerialNumber(self, serialNumber = 'end'):
        self.serialNumber = serialNumber

    def setPeople(self, people = {}):
        self.people = people

    def setTreeItem(self, treeItem):
        self.treeItem = treeItem

    def getId(self):
        return self.id

    def getComSpgmId(self):
        return self.comSpgmId

    def getComFormId(self):
        return self.comFormId

    def getOutDate(self):
        return self.outDate

    def getStation(self):
        return self.station

    def getMilType(self):
        return self.milType

    def getMilUnitName(self):
        return self.milUnitName

    def getSerialNumber(self):
        return self.serialNumber

    def getPeople(self):
        return self.people

    def getPeopleCount(self):
        return len(self.getPeople())

    def identifyTag(self):
        # На команды с идентификатором >360 (ФСО, НГ, МЧС) ПЭКи не печатаются.
        if self.getComSpgmId() > 360:
            tag = 'unprint'
        # Команды, остающиеся на ночёвку, выделяются чёрным.
        elif Datetime.strToDate(self.getOutDate()) > Datetime.getDate():
            tag = 'overnight'
        # Команды, в которых нет людей, выделяются серым.
        elif self.getPeopleCount() < 1:
            tag = 'empty'
        else:
            tag = ''

        return tag

    def getTreeItem(self):
        return self.treeItem

    # Возвращает кортеж свойств команды для отображения в дереве. 
    def getTreeItemValues(self):
        return (
            self.getComSpgmId(),
            self.getComFormId(),
            self.getOutDate(),
            self.getStation(),
            self.getMilType(),
            self.getPeopleCount(),
        )

# Класс описания объекта человека.
class Man:
    # Соответствие статусов заявок на ПЭК и оформления (tag).
    STATUSES = {
        0: 'noRequest',     # заявка не создана
        1: 'draft',         # черновик
        2: 'approve',       # отправлена на согласование
        3: 'inCOD',         # отправлена в ЦОД
        5: 'approved',      # одобрена ЦОД
        6: 'cancelled',     # отклонена ЦОД
        9: 'printed',       # напечатана
        200: 'printing',    # отправлена на печать
        299: 'printError',  # ошибка печати
    }

    def __init__(self, manId, values = {}):
        self.id = manId
        self.setTeamId(values['teamId'])

        self.setPersonalNumber(values['personalNumber'])
        self.setLastName(values.get('lastName', ''))
        self.setFirstName(values.get('firstName', ''))
        self.setMiddleName(values.get('middleName', ''))
        self.setBirthDate(values.get('birthDate', ''))
        self.setStatus(values.get('status', ''))
        self.setPec(values.get('chipId', ''))
        self.setRequestId(values.get('requestId', ''))
        self.setTreeItem(None)

    def __eq__(self, other):
        return (
            self.getId() == other.getId()
            and self.getTeamId() == other.getTeamId()
            and self.getLastName() == other.getLastName()
            and self.getFirstName() == other.getFirstName()
            and self.getMiddleName() == other.getMiddleName()
            and self.getBirthDate() == other.getBirthDate()
            and self.getStatus() == other.getStatus()
            and self.getPec() == other.getPec()
        )

    def setTeamId(self, teamId):
        self.teamId = teamId

    def setPersonalNumber(self, personalNumber):
        self.personalNumber = personalNumber

    def setLastName(self, lastName):
        self.lastName = lastName

    def setFirstName(self, firstName):
        self.firstName = firstName

    def setMiddleName(self, middleName):
        self.middleName = middleName

    def setBirthDate(self, birthDate):
        self.birthDate = birthDate

    def setStatus(self, status):
        self.status = status

    def setPec(self, chipId):
        if chipId:
            self.pec = Pec(chipId = chipId, values = {'manId': self.getId()})
        else:
            self.pec = None

    def setRequestId(self, requestId):
        self.requestId = requestId

    def setTreeItem(self, treeItem):
        self.treeItem = treeItem

    def getId(self):
        return self.id

    def getTeamId(self):
        return self.teamId

    def getPersonalNumber(self):
        return self.personalNumber

    def getLastName(self):
        return self.lastName

    def getFirstName(self):
        return self.firstName

    def getMiddleName(self):
        return self.middleName

    def getBirthDate(self):
        return self.birthDate

    def getStatus(self):
        return self.status

    def getPec(self):
        return self.pec

    def getRequestId(self):
        return self.requestId

    def getTreeItem(self):
        return self.treeItem

    def getFio(self):
        return ' '.join([self.getLastName(), self.getFirstName(), self.getMiddleName()])

    def getManInfo(self):
        return '{fio} {personalNumber} ({requestId})'.format(
            fio = self.getFio(),
            personalNumber = self.getPersonalNumber(),
            requestId = self.getRequestId(),
        )

    def identifyTag(self):
        return self.STATUSES.get(self.getStatus(), 'unknown')

    # Возвращает кортеж свойств человека для отображения в дереве.
    def getTreeItemValues(self):
        return (
            '',
            '',
            '',
            '',
            '',
            self.getManInfo(),
        )

# Класс описания объекта ПЭК.
class Pec:
    def __init__(self, chipId, values = {}):
        self.chipId = chipId
        self.setManId(values['manId'])

        self.setSeries(values.get('series', ''))
        self.setNumber(values.get('number', ''))

    def __eq__(self, other):
        return self.chipId == other.chipId

    def setManId(self, manId):
        self.manId = manId

    def setSeries(self, series):
        self.series = series

    def setNumber(self, number):
        self.number = number

    def getChipId(self):
        return self.chipId

    def getManId(self):
        return self.manId

    def getSeries(self):
        return self.series

    def getNumber(self):
        return self.number
