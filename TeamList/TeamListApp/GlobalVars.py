# Список команд. Переменная необходима в кроссмодульном пространстве имён.
teamList = {}

# Объект Gui-приложения. Переменная необходима в кроссмодульном пространстве имён.
application = None

# Объект сокета.
webSocketServer = None

# Объект клиента, подключающегося к сокету и выполняющего взаимодействие с АС Паспорт.
webSocketClient = None

# Словарь для временного хранения элементов.
temporary = {}

# Объект очереди для отправки заявок на согласование.
approveQueue = None

# Объект очереди для отправки заявок на печать.
printQueue = None