import os
import time

import json
from docxtpl import DocxTemplate
from threading import Thread

import Datetime
import Other
import Db
import Events
import Messenger
import WebSocket as WS
from Pathes import Pathes
from TeamListApp import Gui
from TeamListApp import Data
from TeamListApp import GlobalVars

# Класс для генерации актов.
class Acts:
    # Метод генерации актов. Формирует акты на команду призывников и сохраняет их по соответствующему пути.
    @staticmethod
    def generate(printNow = False):
        try:
            # Получаем выбранную команду.
            team = TeamList.getSelectionTeam()
        except IndexError:
            print('Невозможно сформировать акты: команда не выбрана.')
            return
        except KeyError:
            print('Невозможно сформировать акты: выбранный элемент не является командой.')
            return

        try:
            # Определяем свободные номера в сквозной нумерации.
            freeNumbers = FreeNumbers.get()
        except Exception as e:
            print('Невозможно сформировать акты: ')
            print(e)
            return

        # Получаем информацию по напечатанным ПЭК для всех людей команды.
        PecList.setPecInfo(PecList.getTeamPecs(team))

        # Генерируем массив с данными для подстановки в шаблон MS Word.
        data = {
            'teamNumber': team.getComSpgmId(),
            'milUnitName': team.getMilUnitName(),
            'milType': team.getMilType(),
            'people': [],
        }

        i = 0
        for manId, man in team.getPeople().items():
            # Здесь столбцы названы короткими именами, чтобы не ломать шаблон MS Word.
            manInfo = {
                'i2': man.getFio(),                                                     # fio
                'i3': Datetime.strToDate(man.getBirthDate()).strftime('%Y'),            # birthYear
                'i4': Datetime.getDate().strftime('%d.%m.%Y'),                          # nowDate
                'i5': man.getPec().getSeries() if man.getPec() else '',                 # pecSeries
                'i6': man.getPec().getNumber() if man.getPec() else '',                 # pecNumber
            }

            if len(freeNumbers['free']) < 1:
                newFirst = freeNumbers['first'] + len(team.getPeople()) - i
                freeNumbers['free'].extend(range(freeNumbers['first'], newFirst))
                freeNumbers['first'] = newFirst

            manInfo['i1'] = freeNumbers['free'][0]                                      # generalNumber
            freeNumbers['free'].pop(0)
            i += 1
            manInfo['i7'] = i                                                           # number

            data['people'].append(manInfo)

        # Сохраняем новые значения свободных номеров в сквозной нумерации.
        FreeNumbers.save(freeNumbers['free'], freeNumbers['first'])

        # Получаем путь к директории для сохранения актов. Если она отсутствует, создаём её.
        actDir = Acts.makeDirectories(team.getOutDate())

        # Сохраняем акты.
        templateObject = DocxTemplate(Pathes.getConscriptCommandTemplateFile())
        templateObject.render(data)
        actPath = Acts.getSaveActPath(actDir, team.getComSpgmId(), team.getId())
        templateObject.save(actPath)

        template2Object = DocxTemplate(Pathes.getConscriptCommandTemplate2File())
        template2Object.render(data)
        act2Path = Acts.getSaveAct2Path(actDir, team.getComSpgmId(), team.getId())
        template2Object.save(act2Path)

        # Если стоит чекбокс "Напечатать сразу", отправляем на печать.
        if printNow:
            Acts.printActs([actPath, act2Path])

    # По очереди открывает акты в MS Word и отправляет на печать.
    @staticmethod
    def printActs(acts):
        try:
            for act in acts:
                Other.printDocument(act)
                time.sleep(4)
        except Exception as e:
            print('При печати актов возникла ошибка:')
            print(e)

    # Создаёт нужную директорию для сохранения актов, если её нет, и возвращает путь к ней.
    @staticmethod
    def makeDirectories(outDate):
        outDate = Datetime.strToDate(outDate)
        directory = Pathes.getActsDir() + '{year}\\{month}\\{day}\\'.format(
            year = outDate.strftime('%Y'),
            month = Datetime.getMonthString(outDate.strftime('%m')),
            day = outDate.strftime('%d'),
        )

        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory

    # Возвращает путь для сохранения акта на команду призывников.
    @staticmethod
    def getSaveActPath(directory, teamNumber, teamId):
        return directory + '{number} ({id}) акт на команду.docx'.format(
            number = teamNumber,
            id = teamId,
        )

    # Возвращает путь для сохранения акта 2 на команду призывников.
    @staticmethod
    def getSaveAct2Path(directory, teamNumber, teamId):
        return directory + '{number} ({id}) акт 2 на команду.docx'.format(
            number = teamNumber,
            id = teamId,
        )

# Класс для работы со свободными номерами в сквозной нумерации.
class FreeNumbers:
    # Возвращает путь до файла, в котором хранятся свободные номера.
    @staticmethod
    def getFilePath():
        return Pathes.getActTemplatesDir() + 'freeNumbers.txt'

    # Помечает указанные номера (или диапазоны номеров) как свободные в сквозной нумерации.
    @staticmethod
    def free(newFreeNumbers):
        freeNumbers = FreeNumbers.get()
        diapasones = newFreeNumbers.split(',')

        for diapasone in diapasones:
            diapasone = diapasone.strip()
            numbers = diapasone.split('-')
            if len(numbers) < 2:
                numbers = [numbers[0], numbers[0]]

            for number in range(int(numbers[0]), int(numbers[1]) + 1):
                try:
                    freeNumbers['free'].index(number)
                except ValueError:
                    freeNumbers['free'].append(number)

        FreeNumbers.save(freeNumbers['free'], freeNumbers['first'])

    # Метод считывает из файла и возвращает свободные номера в сквозной нумерации.
    @staticmethod
    def get():
        result = {
            'free': [],
            'first': 1,
        }

        try:
            numberFile = open(FreeNumbers.getFilePath(), 'r')

            for line in numberFile:
                numbers = line.strip().split('-')

                if len(numbers) > 1:
                    if numbers[1] == '...':
                        result['first'] = int(numbers[0])
                        continue
                    else:
                        for number in range(int(numbers[0]), int(numbers[1]) + 1):
                            result['free'].append(number)
                else:
                    result['free'].append(int(numbers[0]))

            numberFile.close()
        except:
            pass

        result['free'].sort()

        return result

    # Метод сохраняет в файл новые значения свободных номеров в сквозной нумерации.
    @staticmethod
    def save(freeNumbers, first):
        numberFile = open(FreeNumbers.getFilePath(), 'w')

        for number in freeNumbers:
            numberFile.write(str(number) + '\n')

        numberFile.write(str(first) + '-...\n')

        numberFile.close()

# Класс для работы со списком команд.
class TeamList:
    # Возвращает список команд.
    @staticmethod
    def getTeamList():
        return GlobalVars.teamList

    # Возвращает объект команды по её идентификатору.
    @staticmethod
    def getTeam(teamId):
        return TeamList.getTeamList()[teamId]

    # Добавляет (либо изменяет) переданную команду в список и отображает её в дереве.
    @staticmethod
    def setTeam(team):
        TeamList.showTeam(team)
        TeamList.getTeamList()[team.getId()] = team

    # Удаляет переданную команду из списка и убирает её из дерева.
    @staticmethod
    def deleteTeam(team):
        TeamList.dropTeam(team)
        TeamList.getTeamList().pop(team.getId())

    # Возвращает объект дерева списка команд.
    @staticmethod
    def getTeamListTree():
        return GlobalVars.application.getMainWindow().getListFrame().getTeamListTree()

    # Отображает переданную команду в дереве.
    # Если команды в дереве нет, она добавляется, иначе - изменяется.
    @staticmethod
    def showTeam(team):
        teamTreeItem = team.getTreeItem()

        if teamTreeItem:
            teamTreeItem.setValues(team.getTreeItemValues())
            teamTreeItem.setTags([team.identifyTag()])
            teamTreeItem.modify()
        else:
            treeItem = Gui.TeamListTreeItem(
                tree = TeamList.getTeamListTree(),
                serialNumber = team.getSerialNumber(),
                text = team.getId(),
                values = team.getTreeItemValues(),
                tags = [team.identifyTag()],
            )

            treeItem.show()
            team.setTreeItem(treeItem)

    # Удаляет переданную команду из дерева.
    @staticmethod
    def dropTeam(team):
        team.getTreeItem().drop()

    # Обновление информации по командам.
    @staticmethod
    def update():
        # Раз в минуту обновляем список команд.
        while True:
            teams = TeamList.getTeamList()
            newTeams = TeamList.getNewTeamList()

            # Удаляем команды, которых нет в обновлённом списке.
            for teamId, team in teams.copy().items():
                if not newTeams.get(teamId):
                    TeamList.deleteTeam(teams[teamId])

            # Отрисовываем только те команды, данные по которым поменялись.
            for teamId, team in newTeams.items():
                # Добавляем команду, если её нет, или обновляем данные команды при необходимости.
                if not teams.get(teamId) or teams[teamId] != team:
                    TeamList.setTeam(team)

            TeamList.getTeamListTree().resetHeight()

            time.sleep(60)

    # Возвращает обновлённый список команд, полученный из БД.
    @staticmethod
    def getNewTeamList():
        teamData = Queries.getTeamList()
        teamList = {}
        serialNumber = 0

        for row in teamData:
            teamList[row[0]] = Data.Team(
                teamId = row[0],
                values = {
                    'comSpgmId': row[1],
                    'comFormId': row[2],
                    'outDate': row[3].strftime('%d.%m.%Y'),
                    'station': row[4],
                    'milType': row[5],
                    'milUnitName': row[6],
                    'serialNumber': serialNumber,
                },
            )

            serialNumber += 1

        return teamList

    # Возвращает команду, выбранную в дереве.
    @staticmethod
    def getSelectionTeam():
        nodeId = TeamList.getTeamListTree().getTree().selection()[0]

        for teamId, team in TeamList.getTeamList().items():
            if team.getTreeItem().getNodeId() == nodeId:
                return team

# Класс для работы со списком людей.
class PeopleList:
    # Возвращает список людей команды по идентификатору команды.
    @staticmethod
    def getPeopleList(teamId):
        return TeamList.getTeam(teamId).getPeople()

    # Возвращает объект человека по идентификатору команды и идентификатору человека.
    @staticmethod
    def getMan(teamId, manId):
        return PeopleList.getPeopleList(teamId)[manId]

    # Добавляет (либо изменяет) переданного человека в список и отображает его в дереве.
    @staticmethod
    def setMan(man):
        PeopleList.showMan(man)
        PeopleList.getPeopleList(man.getTeamId())[man.getId()] = man

    # Удаляет переданного человека из списка и убирает его из дерева.
    @staticmethod
    def deleteMan(man):
        PeopleList.dropMan(man)
        PeopleList.getPeopleList(man.getTeamId()).pop(man.getId())

    # Отображает переданного человека в дереве.
    # Если человека в дереве нет, он добавляется, иначе - изменяется.
    @staticmethod
    def showMan(man):
        teamTreeItem = TeamList.getTeam(man.getTeamId()).getTreeItem()
        manTreeItem = man.getTreeItem()

        if manTreeItem:
            manTreeItem.setValues(man.getTreeItemValues())
            manTreeItem.setTags([man.identifyTag()])
            manTreeItem.modify()
        else:
            treeItem = Gui.TeamListTreeItem(
                tree = TeamList.getTeamListTree(),
                parent = teamTreeItem.getNodeId(),
                values = man.getTreeItemValues(),
                tags = [man.identifyTag()]
            )

            treeItem.show()
            man.setTreeItem(treeItem)

    # Удаляет переданного человека из дерева.
    @staticmethod
    def dropMan(man):
        man.getTreeItem.drop()

    # Обновление информации по людям.
    @staticmethod
    def update():
        # Раз в 5 секунд обновляем информацию по людям.
        while True:
            teams = TeamList.getTeamList()
            teamIds = [teamId for teamId in teams.keys()]
            people = PeopleList.getNewPeopleList(teamIds)
            needUpdateTeamIds = []

            # Удаляем людей, которых нет в обновлённом списке.
            for teamId, team in teams.items():
                for manId, man in team.getPeople().items():
                    if not people.get(manId):
                        needUpdateTeamIds.append(teamId)
                        PeopleList.deleteMan(man)

            # Отрисовываем только тех людей, данные по которым были изменены.
            for manId, man in people.items():
                oldMan = teams[man.getTeamId()].getPeople().get(manId)
                # Добавляем человека, если его нет или обновляем данные человека при необходимости.
                if not oldMan or oldMan != man:
                    needUpdateTeamIds.append(man.getTeamId())
                    PeopleList.setMan(man)

            needUpdateTeamIds = list(set(needUpdateTeamIds))

            # Если количество людей в команде изменялось, обновляем строку команды.
            for teamId in needUpdateTeamIds:
                TeamList.showTeam(teams[teamId])

            time.sleep(5)

    # Возвращает обновлённый (полученный из БД) список людей по переданным идентификаторам команд.
    @staticmethod
    def getNewPeopleList(teamIds):
        peopleData = Queries.getPeopleList(teamIds)
        people = {}
        personalNumbers = {}

        for row in peopleData:
            man = Data.Man(
                manId = row[0],
                values = {
                    'teamId': row[6],
                    'personalNumber': row[4],
                    'lastName': row[1],
                    'firstName': row[2],
                    'middleName': row[3],
                    'birthDate': row[5].strftime('%d.%m.%Y'),
                },
            )

            if personalNumbers.get(man.getPersonalNumber()):
                personalNumbers[man.getPersonalNumber()].append(man.getId())
            else:
                personalNumbers[man.getPersonalNumber()] = [man.getId()]

            people[man.getId()] = man

        # Определяем статусы людей.
        statusesData = Queries.getPeopleRequestStatuses(personalNumbers.keys())

        for row in statusesData:
            for manId in personalNumbers.copy().get(row[0], []):
                # Проверяем соответствие людей.
                # Необходима для ситуации, когда несколько человек имеют один личный номер.
                if PeopleList.isManEqual(people[manId], row):
                    people[manId].setStatus(row[5])
                    people[manId].setPec(str(row[6]).lower())
                    people[manId].setRequestId(str(row[7]))
                    personalNumbers[row[0]].remove(manId)
                    break

            if len(personalNumbers.get(row[0], [])) > 0:
                print('По следующим людям не удалось получить статус заявки:')
                for manId in personalNumbers[row[0]]:
                    man = people[manId]
                    print('{manId} (команда {teamId}) {fio} {personalNumber}'.format(
                        manId = man.getId(),
                        teamId = man.getTeamId(),
                        fio = man.getFio(),
                        personalNumber = man.getPersonalNumber(),
                    ))

        return people

    # Проверяет, совпадают ли значения человека в объекте и в списке.
    @staticmethod
    def isManEqual(man, data):
        return (
            man.getLastName() == data[1]
            and man.getFirstName() == data[2]
            and man.getMiddleName() == data[3]
            and man.getBirthDate() == data[4].strftime('%d.%m.%Y')
        )

    @staticmethod
    def findPeopleByStatus(status):
        people = {}
        for team in TeamList.getTeamList().values():
            for manId, man in team.getPeople().items():
                if man.getStatus() == status:
                    people[manId] = man

        return people

    @staticmethod
    def findManByRequestId(requestId):
        for team in TeamList.getTeamList().values():
            for manId, man in team.getPeople().items():
                if man.getRequestId() == requestId:
                    return man

# Класс для работы со списком ПЭК.
class PecList:
    # Возвращает массив объектов типа Data.Pec для всех людей переданной команды.
    @staticmethod
    def getTeamPecs(team):
        pecs = {}

        for manId, man in team.getPeople().items():
            pec = man.getPec()

            if pec:
                pecs[pec.getChipId()] = pec

        return pecs

    # Получает информацию (серия и номер) по ПЭКам и устанавливает её в переданные объекты.
    @staticmethod
    def setPecInfo(pecs):
        if len(pecs) < 1:
            return {}

        data = Queries.getPecList([str(chipId) for chipId in pecs.keys()])
        result = {}

        for row in data:
            pec = pecs[row[0]]

            pec.setSeries(row[1])
            pec.setNumber(row[2])

# Класс для работы со статистикой.
class Statistics:
    # Возвращает объект фрейма, в котором размещаются данные статистики.
    @staticmethod
    def getStatisticsFrame():
        return GlobalVars.application.getMainWindow().getBottomFrame().getStatisticsFrame()

    # Обновление данных статистики.
    @staticmethod
    def update():
        # Раз в 10 секунд обновляем данные статистики.
        while True:
            data = {key: 0 for key in Gui.StatisticsFrame.LABEL_NAMES.keys()}
            statusesData = Queries.getLocalPeopleStatuses()
            localStatuses = {row[0]: row[1] for row in statusesData}

            for teamId, team in TeamList.getTeamList().items():
                for manId, man in team.getPeople().items():
                    if man.getStatus() == 3:
                        data['inCod'] += 1

                    if team.identifyTag() != 'unprint':
                        data['needPrint'] += 1

                        if man.getStatus() == 9:
                            data['printed'] += 1
                        else:
                            data['remainPrint'] += 1

                    if localStatuses.get(manId):
                        data['remainAll'] += 1

                        if localStatuses[manId] == 1:
                            data['notSelected'] += 1
                        elif localStatuses[manId] == 2:
                            data['free'] += 1
                        elif localStatuses[manId] == 7:
                            data['selected'] += 1

            for key, value in data.items():
                Statistics.getStatisticsFrame().setValue(key, value)

            time.sleep(10)

# Класс для выполнения запросов к БД.
class Queries:
    # Получает список команд.
    @staticmethod
    def getTeamList():
        cursor = Db.Conscript().getCursor()
        cursor.execute('''
            SELECT
                T_Out.ID_Out,
                T_ComForm.ID_ComSPgM,
                T_ComForm.ID_ComForm,
                T_Out.OutDate,
                S_Station.Name,
                S_MilType.Name,
                S_MilUnit.Name
            FROM T_Out
                INNER JOIN T_ComForm ON T_ComForm.ID_ComForm = T_Out.ID_ComForm
                INNER JOIN S_MilUnit ON S_MilUnit.ID_MilUnit = T_ComForm.ID_MilUnit
                INNER JOIN S_Station ON S_Station.ID_Station = S_MilUnit.ID_Station
                INNER JOIN T_ComSPgM ON T_ComSPgM.ID_ComSPgM = T_ComForm.ID_ComSPgM
                INNER JOIN T_ComMVO ON T_ComMVO.ID_ComMVO = T_ComSPgM.ID_ComMVO
                INNER JOIN S_MilType ON S_MilType.ID_MilType = T_ComMVO.ID_MilType
            WHERE DATEDIFF(d, CONVERT(DATETIME, '{date}', 104), T_Out.OutDate) >= 0
            ORDER BY T_ComSPgM.ID_ComSPgM
        '''.format(date = Datetime.getDate().strftime('%d.%m.%Y')))

        return cursor.fetchall()

    # Получает список людей по переданному списку идентификаторов команд.
    @staticmethod
    def getPeopleList(teamIds):
        if (len(teamIds) < 1):
            return []

        cursor = Db.Conscript().getCursor()
        cursor.execute('''
            SELECT
                T_People.ID_People,
                T_People.LastN,
                T_People.FirstN,
                T_People.MiddleN,
                T_People.Note,
                T_People.BirthDate,
                T_Out.ID_Out
            FROM T_People
                INNER JOIN T_Log ON T_People.ID_People = T_Log.ID_People
                INNER JOIN T_Out ON T_Out.ID_ComForm = T_Log.ID_ComForm
            WHERE T_Out.ID_Out IN ('{teamIds}')
                AND T_Log.ID_State = 9
        '''.format(teamIds = '\', \''.join(str(value) for value in teamIds)))

        return cursor.fetchall()

    # Получает статусы заявок на ПЭК для людей по переданному списку личных номеров.
    @staticmethod
    def getPeopleRequestStatuses(personalNumbers):
        if len(personalNumbers) < 1:
            return []

        cursor = Db.Objreq().getCursor()
        cursor.execute('''
            SELECT
                req_info.pers_number,
                req_info.last_name,
                req_info.first_name,
                req_info.second_name,
                req_info.birth_date,
                request.status,
                req_info.chip_id,
                request.id
            FROM requests.req_info
                INNER JOIN requests.request ON req_info.request_id = request.id
            WHERE req_info.pers_number IN ('{personalNumbers}')
        '''.format(personalNumbers = '\', \''.join(str(value) for value in personalNumbers)))

        return cursor.fetchall()

    # Получает информацию по ПЭКам по переданному списку идентификаторов чипов ПЭК.
    @staticmethod
    def getPecList(chipIds):
        if len(chipIds) < 1:
            return []

        cursor = Db.Pec().getCursor()
        cursor.execute('''
            SELECT blank.chipid, blank.series, blank.number
            FROM public.blank
            WHERE blank.chipid IN ('{chipIds}')
        '''.format(chipIds = '\', \''.join(value for value in chipIds)))

        return cursor.fetchall()

    # Получает локальные статусы (ВКгМ) по всем людям.
    @staticmethod
    def getLocalPeopleStatuses():
        cursor = Db.Conscript().getCursor()
        cursor.execute('''
            SELECT T_Log.ID_People, S_State.ID_StateGroup
            FROM T_Log
                INNER JOIN S_State ON  S_State.ID_State = T_Log.ID_State
            WHERE DATEDIFF(d, CONVERT(DATETIME, '{date}', 104), T_Log.Event) >= 0
                AND S_State.ID_StateGroup IN (1, 2, 7)
            ORDER BY T_Log.Event ASC
        '''.format(date = Datetime.getDate().strftime('%d.%m.%Y')))

        return cursor.fetchall()

# Класс для работы с сокетом.
class WebSocketServer:
    @staticmethod
    def getName():
        return 'server'

    @staticmethod
    def getServer():
        return GlobalVars.webSocketServer

    @staticmethod
    def openSocket():
        GlobalVars.webSocketServer = WS.Server(
            host = WebSocketServer.getHost(),
            port = WebSocketServer.getPort(),
            listen = WebSocketServer.getListen(),
            handlerFunctions = {
                'onOpen': WebSocketServer.onOpen,
                'onOpenError': WS.Server.onOpenError,
                'onConnect': WebSocketServer.onConnect,
                'onConnectError': WS.Server.onConnectError,
            },
        )

        WebSocketServer.getServer().openSocket()

    @staticmethod
    def getHost():
        return ''

    @staticmethod
    def getPort():
        return 1635

    @staticmethod
    def getListen():
        return 1

    @staticmethod
    def onOpen(event, sock):
        WS.Server.onOpen(event, sock)
        Thread(target = WebSocketLocalClient.start).start()

    @staticmethod
    def onConnect(event, sock, connection):
        Thread(target = WebSocketServer.prepareConnection, args = (sock, connection,)).start()

    @staticmethod
    def prepareConnection(sock, connection):
        clientName = WebSocketServer.identifyClient(connection)
        sock.addRout(clientName, connection.getAddress())

        connection.setHandlers({
            'onGetData': WebSocketServer.onGetData,
            'onSendError': WebSocketServer.onSendError,
            'onNotDelivered': WebSocketServer.onNotDelivered,
        })

        connection.waitingData()

    @staticmethod
    def identifyClient(connection):
        data = connection.getConnection().recv(1024)
        return data.decode(WS.Connection.getEncoding())

    @staticmethod
    def onGetData(event, connection, data):
        # Если не удалось распознать сообщение, предполагаем, что это только часть сообщения
        # и записываем его в массив временных данных.
        if GlobalVars.temporary.get(connection.getAddress()):
            data += GlobalVars.temporary[connection.getAddress()]
            GlobalVars.temporary.pop(connection.getAddress())

        try:
            message = Messenger.Message.fromJson(data)
        except json.JSONDecodeError:
            GlobalVars.temporary[connection.getAddress()] = data
            return

        Thread(target = WebSocketServer.prepareMessage, args = (connection, message,)).start()

    @staticmethod
    def onSendError(event, exception, connection, data):
        print('Сокету не удалось отправить по адресу {address} следующие данные: \'\'\'{data}\'\'\'. Ошибка:'.format(
            address = connection.getAddress(),
            data = data,
        ))
        print(exception)

    @staticmethod
    def prepareMessage(connection, message):
        if message.getToName() == WebSocketServer.getName():
            return

        sock = WebSocketServer.getServer()
        connectionAddress = sock.getRoute(message.getToName())

        if connectionAddress:
            sock.getConnection(connectionAddress).sendMessage(message)
        else:
            connection.getEvent('onNotDelivered').execute(
                connection = connection,
                message = message,
                cause = '404:Адресат не найден среди подключений сокета.'
            )

    @staticmethod
    def onNotDelivered(event, connection, message, cause):
        if message.getFromName() == WebSocketLocalClient.getName():
            WebSocketLocalClient.onNotDelivered(event, connection, message, cause)

# Класс для работы с локальным клиентом сокета.
class WebSocketLocalClient:
    @staticmethod
    def getName():
        return 'localClient'

    @staticmethod
    def getApprovePageName():
        return 'approvePage'

    @staticmethod
    def getPrintPageName():
        return 'printPage'

    @staticmethod
    def getClient():
        return GlobalVars.webSocketClient

    @staticmethod
    def start():
        WebSocketLocalClient.connect()

        WebSocketLocalClient.main()

    @staticmethod
    def connect():
        GlobalVars.webSocketClient = WS.Client(
            host = WebSocketLocalClient.getHost(),
            port = WebSocketLocalClient.getPort(),
            handlerFunctions = {
                'onConnect': WebSocketLocalClient.onConnect,
            },
        )

        WebSocketLocalClient.getClient().connect()

    @staticmethod
    def getHost():
        return '127.0.0.1'

    @staticmethod
    def getPort():
        return WebSocketServer.getPort()

    @staticmethod
    def onConnect(event, connection):
        connection.setHandlers({
            'onGetData': WebSocketLocalClient.onGetData,
        })

        print('{name} подключился к сокету.'.format(name = WebSocketLocalClient.getName()))

        connection.send(WebSocketLocalClient.getName())

    @staticmethod
    def main():
        GlobalVars.approveQueue = ApprovePrintQueue()
        Thread(
            target = WebSocketLocalClient.queue,
            args = (WebSocketLocalClient.getApproveQueue(), 2, WebSocketLocalClient.getApprovePageName()),
        ).start()
        Thread(
            target = WebSocketLocalClient.waitingResponse,
            args = (WebSocketLocalClient.getApproveQueue()),
        ).start()

        GlobalVars.printQueue = ApprovePrintQueue()
        Thread(
            target = WebSocketLocalClient.queue,
            args = (WebSocketLocalClient.getPrintQueue(), 5, WebSocketLocalClient.getPrintPageName()),
        ).start()
        Thread(
            target = WebSocketLocalClient.waitingResponse,
            args = (WebSocketLocalClient.getPrintQueue()),
        ).start()

    @staticmethod
    def getApproveQueue():
        return GlobalVars.approveQueue

    @staticmethod
    def getPrintQueue():
        return GlobalVars.printQueue

    @staticmethod
    def queue(queueObj, status, pageName):
        while True:
            time.sleep(queueObj.getDelay())

            for manId, man in PeopleList.findPeopleByStatus(status).items():
                queueObj.add(man.getRequestId())

            requestId = queueObj.progress()

            if not requestId:
                continue

            WebSocketLocalClient.getClient().getConnection().sendMessage(Messenger.Message(
                fromName = WebSocketLocalClient.getName(),
                toName = pageName,
                message = str(requestId),
            ))

    @staticmethod
    def onNotDelivered(event, connection, message, cause):
        errorCode = cause.split(':')[0]

        if errorCode == '404':
            if message.getToName() == WebSocketLocalClient.getApprovePageName():
                WebSocketLocalClient.getApproveQueue().reprogress(message.getMessage())
            else:
                WebSocketLocalClient.getPrintQueue().reprogress(message.getMessage())
        else:
            if message.getToName() == WebSocketLocalClient.getApprovePageName():
                WebSocketLocalClient.getApproveQueue().error(message.getMessage())
            else:
                WebSocketLocalClient.getPrintQueue().error(message.getMessage())

    @staticmethod
    def waitingResponse(queueObj):
        WebSocketLocalClient.getClient().getConnection().waitingData()

    @staticmethod
    def onGetData(event, connection, data):
        try:
            message = Messenger.Message.fromJson(data)
        except json.JSONDecodeError:
            print('Произошла ошибка при получении ответа.')
            return

        Thread(target = WebSocketLocalClient.prepareMessage, args = (message,)).start()

    @staticmethod
    def prepareMessage(message):
        data = json.loads(message.getMessage())
        if message.getFromName() == WebSocketLocalClient.getApprovePageName():
            queueObj = WebSocketLocalClient.getApproveQueue()
        elif message.getFromName() == WebSocketLocalClient.getPrintPageName():
            queueObj = WebSocketLocalClient.getPrintQueue()
        else:
            print('{localClient} не смог распознать адресанта сообщения.'. format(
                localClient = WebSocketLocalClient.getName(),
            ))
            return

        try:
            if data['status'] == 'success':
                queueObj.success(data['requestId'])
            elif data['status'] == 'cancelled':
                queueObj.error(data['requestId'])
                print('Заявка {manInfo} отклонена ЦОД.'.format(
                    manInfo = PeopleList.findManByRequestId(data['requestId']).getManInfo(),
                ))
            elif data['status'] == 'error':
                queueObj.error(data['requestId'])
                print(data['message'])
        except Exception as e:
            print('Ошибка при обработке сообщения локальным клиентом:')
            print(e)

# Класс очереди.
class ApprovePrintQueue:
    def __init__(self, delay = 60):
        self.queue = []
        self.priority = []
        self.processing = []
        self.success = []
        self.errors = []
        self.delay = delay

    # Проверяет, присутствует ли элемент в обычной очереди или в состоянии обработки.
    def has(self, element):
        try:
            self.queue.index(element)
            return True
        except ValueError:
            return self.hasProcessing(element)

    # Проверяет, присутствует ли элемент в приоритетной очереди или в состоянии обработки.
    def hasPriority(self, element):
        try:
            self.priority.index(element)
            return True
        except ValueError:
            return self.hasProcessing(element)

    # Проверяет, находится ли предмет в состоянии обработки.
    def hasProcessing(self, element):
        try:
            self.processing.index(element)
            return True
        except ValueError:
            return False

    # Добавляет элемент в обычную очередь.
    def add(self, element):
        if self.has(element):
            return

        self.queue.append(element)

    # Возвращает элемент из обычной очереди и удаляет его из очереди.
    def get(self):
        return self.queue.pop(0)

    # Проверяет, не пуста ли обычная очередь.
    def isNotEmpty(self):
        return len(self.queue) > 0

    # Добавляет элемент в приоритетную очередь.
    def addPriority(self, element):
        if self.hasPriority(element):
            return

        self.priority.append(element)

    # Возвращает элемент из приоритетной очереди и удаляет его из очереди.
    def getPriority(self):
        return self.priority.pop(0)

    # Проверяет, не пуста ли приоритетная очередь.
    def isNotEmptyPriority(self):
        return len(self.priority) > 0

    # Переводит элемент из обычной очереди в состояние обработки.
    def progressElement(self):
        element = self.get()
        self.processing.append(element)
        return element

    # Переводит элемент из приоритетной очереди в состояние обработки.
    def progressPriority(self):
        element = self.getPriority()
        self.processing.append(element)
        return element

    # Переводит элемент из состояния обработки в состояние успеха.
    def success(self, element):
        self.processing.remove(element)
        self.success.append(element)
        return element

    # Переводит элемент из состояния обработки в состояние ошибки.
    def error(self, element):
        self.processing.remove(element)
        self.errors.append(element)
        return element

    # Переводит элемент из состояния обработки в приоритетную очередь.
    def reprogress(self, element):
        self.processing.remove(element)
        self.addPriority(element)
        return element

    # Отправляет элемент в состояние обработки, если приоритетная очередь не пуста, то из приоритетной очереди,
    # иначе - из обычной очереди. Если обычная очередь также пуста, процесс не блокируется.
    def progress(self):
        if self.isNotEmptyPriority():
            return self.progressPriority()

        if self.isNotEmpty():
            return self.progressElement()

        return None

    def getDelay(self):
        return self.delay
