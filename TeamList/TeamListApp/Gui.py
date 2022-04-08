import tkinter as tk
from tkinter import ttk

import Other
from TeamListApp import Handlers

# Класс приложения.
class Application:
    def __init__(self):
        self._loadWindows()

    def _loadWindows(self):
        self.mainWindow = MainWindow()

    def getMainWindow(self):
        return self.mainWindow

    def show(self):
        self.getMainWindow().getWindow().mainloop()

    # Возвращает код основного цвета фона приложения.
    @staticmethod
    def getBaseBackgroundColor():
        return Other.getColorCode('lightBlue')

# Класс основного окна приложения.
class MainWindow:
    def __init__(self):
        self._loadWindow()

    def _loadWindow(self):
        self.window = tk.Tk()
        self.window.update_idletasks()
        self.window['background'] = Application.getBaseBackgroundColor()
        self.window.title('Информация по командам')
        self.window.geometry('+0+0')
        self.window.resizable(width = False, height = True)

        self._loadTopFrame()
        self._loadListFrame()
        self._loadBottomFrame()

    def _loadTopFrame(self):
        self.topFrame = TopFrame(self.getWindow())

    def _loadListFrame(self):
        self.listFrame = TeamListFrame(self.getWindow())

    def _loadBottomFrame(self):
        self.bottomFrame = BottomFrame(self.getWindow())

    def getWindow(self):
        return self.window

    def getTopFrame(self):
        return self.topFrame

    def getListFrame(self):
        return self.listFrame

    def getBottomFrame(self):
        return self.bottomFrame

# Класс верхнего фрейма основного окна приложения.
class TopFrame:
    def __init__(self, master):
        self.master = master
        self._loadFrame()

    def _loadFrame(self):
        self.frame = tk.Frame(
            master = self.getMaster(),
            name = 'topFrame',
            background = Application.getBaseBackgroundColor(),
            padx = 10,
            pady = 5,
        )
        self.frame.grid(row = 0, column = 0, sticky = 'nswe')

        self._loadActsFrame()
        self._loadFreeNumbersFrame()

    def _loadActsFrame(self):
        self.actsFrame = ActsFrame(self.getFrame())

    def _loadFreeNumbersFrame(self):
        self.freeNumbersFrame = FreeNumbersFrame(self.getFrame())

    def getMaster(self):
        return self.master

    def getFrame(self):
        return self.frame

    def getActsFrame(self):
        return self.actsFrame

    def getFreeNumbersFrame(self):
        return self.freeNumbersFrame

# Класс фрейма главного окна приложения для генерации актов (кнопка и чекбокс).
class ActsFrame:
    def __init__(self, master):
        self.master = master
        self.printNow = tk.BooleanVar()
        self._loadFrame()

    def _loadFrame(self):
        self.frame = tk.Frame(
            master = self.getMaster(),
            name = 'generateActsFrame',
            background = Application.getBaseBackgroundColor(),
        )
        self.frame.pack(side = tk.LEFT)

        self.generateActsButton = tk.Button(
            master = self.getFrame(),
            name = 'generateActsButton',
            text = 'Сформировать акты',
            command = self.generateActs,
            relief = tk.RAISED
        )
        self.generateActsButton.pack(side = tk.LEFT, padx = 10)

        self.printNowCheckbox = tk.Checkbutton(
            master = self.getFrame(),
            name = 'printNowCheckbox',
            text = 'Напечатать сразу',
            variable = self.printNow,
            background = Application.getBaseBackgroundColor(),
        )
        self.printNowCheckbox.pack(side = tk.LEFT, padx = 10)

    def generateActs(self):
        Handlers.Acts.generate(printNow = self.isPrintNow())

    def getMaster(self):
        return self.master

    def getFrame(self):
        return self.frame

    def getGenerateActsButton(self):
        return self.generateActsButton

    def getprintNowCheckbox(self):
        return self.printNowCheckbox

    def isPrintNow(self):
        return self.printNow.get()

# Класс фрейма главного окна приложения для освобождения номеров (кнопка и текстовое поле).
class FreeNumbersFrame:
    def __init__(self, master):
        self.master = master
        self.newFreeNumbers = tk.StringVar()
        self._loadFrame()

    def _loadFrame(self):
        self.frame = tk.Frame(
            master = self.getMaster(),
            name = 'freeNumbersFrame',
            background = Application.getBaseBackgroundColor(),
        )
        self.frame.pack(side = tk.RIGHT)

        self.freeNumbersButton = tk.Button(
            master = self.getFrame(),
            name = 'freeNumbersButton',
            text = 'Освободить номера',
            command = self.doFreeNumbers,
            relief = tk.RAISED
        )
        self.freeNumbersButton.pack(side = tk.RIGHT, padx = 10)

        self.freeNumbersEntry = tk.Entry(
            master = self.getFrame(),
            name = 'freeNumbersEntry',
            textvariable = self.newFreeNumbers
        )
        self.freeNumbersEntry.pack(side = tk.RIGHT, padx = 10)

    def doFreeNumbers(self):
        Handlers.FreeNumbers.free(self.getNewFreeNumbers())

    def getMaster(self):
        return self.master

    def getFrame(self):
        return self.frame

    def getFreeNumbersButton(self):
        return self.freeNumbersButton

    def getFreeNumbersEntry(self):
        return self.freeNumbersEntry

    def getNewFreeNumbers(self):
        return self.newFreeNumbers.get()

# Класс фрейма главного окна приложения для отображения списка команд.
class TeamListFrame:
    def __init__(self, master):
        self.master = master
        self._loadFrame()

    def _loadFrame(self):
        self.frame = tk.Frame(master = self.getMaster(), name = 'teamListFrame')
        self.frame.grid(row = 1, column = 0, sticky = 'nswe', padx = 10, pady = 5)

        self._loadTeamListTree()

    def _loadTeamListTree(self):
        self.teamListTree = TeamListTree(self.getFrame())

    def getMaster(self):
        return self.master

    def getFrame(self):
        return self.frame

    def getTeamListTree(self):
        return self.teamListTree

# Класс виджета списка команд.
class TeamListTree:
    def __init__(self, master):
        self.master = master
        self._loadTree()

    def _loadTree(self):
        self.tree = ttk.Treeview(
            master = self.getMaster(),
            name = 'teamListTree',
            columns = ('idComSpgm', 'idComForm', 'outDate', 'stationName', 'milType', 'people'),
            selectmode = 'extended',
            height = 15,
        )
        self.tree.pack(side = tk.LEFT)

        self._loadTreeHeads()
        self._loadTreeColumns()
        self._loadTreeTags()

    def _loadTreeHeads(self):
        self.getTree().heading('#0', text = 'idOut', anchor = 'center')
        self.getTree().heading('idComSpgm', text = 'idComSpgm', anchor = 'center')
        self.getTree().heading('idComForm', text = 'idComForm', anchor = 'center')
        self.getTree().heading('outDate', text = 'Дата отправки', anchor = 'center')
        self.getTree().heading('stationName', text = 'Станция назначения', anchor = 'center')
        self.getTree().heading('milType', text = 'Войска', anchor = 'center')
        self.getTree().heading('people', text = 'Люди', anchor = 'w')

    def _loadTreeColumns(self):
        self.getTree().column('#0', minwidth = 40, width = 40, anchor = 'center')
        self.getTree().column('idComSpgm', minwidth = 75, width = 75, anchor = 'center')
        self.getTree().column('idComForm', minwidth = 75, width = 75, anchor = 'center')
        self.getTree().column('outDate', minwidth = 100, width = 100, anchor = 'center')
        self.getTree().column('stationName', minwidth = 200, width = 200, anchor = 'center')
        self.getTree().column('milType', minwidth = 100, width = 100, anchor = 'center')
        self.getTree().column('people', minwidth = 400, width = 400, anchor = 'w')

    def _loadTreeTags(self):
        self.getTree().tag_configure(
            'unprint',
            background = Other.getColorCode('blue'),
            foreground = Other.getColorCode('red'),
        )
        self.getTree().tag_configure(
            'overnight',
            background = Other.getColorCode('black'),
            foreground = Other.getColorCode('white'),
        )
        self.getTree().tag_configure('empty', background = Other.getColorCode('gray'))
        self.getTree().tag_configure('noRequest', background = Other.getColorCode('brown'))
        self.getTree().tag_configure('draft', background = Other.getColorCode('orange'))
        self.getTree().tag_configure('approve', background = Other.getColorCode('white'))
        self.getTree().tag_configure('inCOD', background = Other.getColorCode('yellow'))
        self.getTree().tag_configure('approved', background = Other.getColorCode('lightGreen'))
        self.getTree().tag_configure('cancelled', background = Other.getColorCode('red'))
        self.getTree().tag_configure('printed', background = Other.getColorCode('green'))
        self.getTree().tag_configure('printing', background = Other.getColorCode('purple'))
        self.getTree().tag_configure('printError', background = Other.getColorCode('gray'))
        self.getTree().tag_configure(
            'unknown',
            background = Other.getColorCode('black'),
            foreground = Other.getColorCode('white'),
        )

    def _loadScrollbar(self):
        self.scrollbar = tk.Scrollbar(master = master, orient = tk.VERTICAL, command = self.getTree().yview)
        self.getTree()['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(side = tk.LEFT, fill = tk.Y)

    # Метод увеличивает или уменьшает высоту виджета при необходимости.
    # Минимальная высота - 15 элементов, максимальная - 25.
    def resetHeight(self):
        rootElementsCount = len(self.getTree().get_children(''))

        if 15 <= rootElementsCount <= 25:
            self.getTree()['height'] = rootElementsCount

    def getMaster(self):
        return self.master

    def getTree(self):
        return self.tree

    def getScrollbar(self):
        return self.scrollbar

# Класс элемента дерева для отображения в виджете списка команд.
class TeamListTreeItem:
    def __init__(self, tree, nodeId = '', parent = '', serialNumber = 'end', text = '', values = (), tags = []):
        self.tree = tree
        self.nodeId = nodeId
        self.parent = parent
        self.serialNumber = serialNumber

        self.setText(text)
        self.setValues(values)
        self.setTags(tags)

    def setText(self, text = ''):
        self.text = text

    def setValues(self, values = ()):
        self.values = values

    def setTags(self, tags = []):
        self.tags = tags

    def getTree(self):
        return self.tree

    def getNodeId(self):
        return self.nodeId

    def getParent(self):
        return self.parent

    def getSerialNumber(self):
        return self.serialNumber

    def getText(self):
        return self.text

    def getValues(self):
        return self.values

    def getTags(self):
        return self.tags

    # Метод добавляет элемент в дерево и отображает его.
    def show(self):
        self.nodeId = self.getTree().getTree().insert(
            self.getParent(),
            self.getSerialNumber(),
            text = self.getText(),
            values = self.getValues(),
            tags = self.getTags(),
        )

        return self.getNodeId()

    # Метод изменяет отображение уже существующего элемента дерева.
    def modify(self):
        self.getTree().getTree().item(
            self.getNodeId(),
            text = self.getText(),
            values = self.getValues(),
            tags = self.getTags(),
        )

    # Метод удаляет элемент из дерева.
    def drop(self):
        self.getTree().getTree().delete(self.getNodeId())

# Класс нижнего фрейма главного окна приложения.
class BottomFrame:
    def __init__(self, master):
        self.master = master
        self._loadFrame()

    def _loadFrame(self):
        self.frame = tk.Frame(
            master = self.getMaster(),
            name = 'bottomFrame',
            background = Application.getBaseBackgroundColor(),
            padx = 10,
            pady = 5,
        )
        self.frame.grid(row = 2, column = 0, sticky = 'nswe')

        self._loadStatisticsFrame()

    def _loadStatisticsFrame(self):
        self.statisticsFrame = StatisticsFrame(self.getFrame())

    def getMaster(self):
        return self.master

    def getFrame(self):
        return self.frame

    def getStatisticsFrame(self):
        return self.statisticsFrame

# Класс фрейма главного окна приложения для отображения статистики.
class StatisticsFrame:
    LABEL_NAMES = {
        'remainAll': 'Осталось всего:',
        'notSelected': 'Не отобранные:',
        'free': 'Свободные:',
        'selected': 'В командах:',
        'needPrint': 'Нужно напечатать:',
        'printed': 'Напечатано:',
        'remainPrint': 'Осталось напечатать:',
        'inCod': 'В ЦОДе:',
    }

    def __init__(self, master):
        self.master = master
        self._loadFrame()

    def _loadFrame(self):
        self.frame = tk.Frame(
            master = self.getMaster(),
            name = 'statisticsFrame',
            background = Application.getBaseBackgroundColor(),
        )
        self.frame.pack(side = tk.LEFT)

        self._setData()
        self.setDefault()

        self._loadLabels()

    # Инициализирует tk-переменные для каждой метки.
    def _setData(self):
        self.data = {key: tk.StringVar() for key in self.LABEL_NAMES.keys()}

    # Устанавливает во все переменные меток значения по умолчанию.
    def setDefault(self):
        for variable in self.getData().values():
            variable.set('Информация обновляется')

    # Устанавливает в переданную метку переданное значение.
    def setValue(self, variable, value):
        self.getVariable(variable).set(value)

    # Загружает и отображает все метки.
    def _loadLabels(self):
        self.labels = {}
        i = 0
        for key, value in self.LABEL_NAMES.items():
            labelName = key + 'Label'
            dataName = key + 'Data'

            self.labels[labelName] = tk.Label(
                master = self.getFrame(),
                name = labelName,
                text = value,
                background = Application.getBaseBackgroundColor(),
            )
            self.getLabels()[labelName].grid(row = i, column = 0, sticky = 'e')

            self.labels[dataName] = tk.Label(
                master = self.getFrame(),
                name = dataName,
                text = '',
                textvariable = self.getVariable(key),
                background = Application.getBaseBackgroundColor(),
            )
            self.getLabels()[dataName].grid(row = i, column = 1, sticky = 'w')

            i += 1

    def getMaster(self):
        return self.master

    def getFrame(self):
        return self.frame

    # Возвращает массив tk-переменных, привязанных ко всем меткам.
    def getData(self):
        return self.data

    # Возвращает tk-переменную, привязанную к переданной метке.
    def getVariable(self, key):
        return self.getData()[key]

    # Возвращает значение tk-переменной, привязанной к переданной метке.
    def getValue(self, key):
        return self.getVariable(key).get()

    def getLabels(self):
        return self.labels
