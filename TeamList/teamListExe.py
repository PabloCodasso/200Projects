try:
    import time
    from threading import Thread
    import TeamListApp
    from TeamListApp import GlobalVars

    def loadGui():
        GlobalVars.application = TeamListApp.Gui.Application()
        GlobalVars.application.show()

    # Загружаем окно приложения.
    Thread(target = loadGui).start()

    time.sleep(0.5)
    # Запускаем обновление информации по командам.
    Thread(target = TeamListApp.Handlers.TeamList.update).start()

    time.sleep(0.5)
    # Запускаем обновление информации по людям.
    Thread(target = TeamListApp.Handlers.PeopleList.update).start()

    time.sleep(5)
    # Запускаем обовление статистики.
    Thread(target = TeamListApp.Handlers.Statistics.update).start()

    # Запускаем работу сокета.
    Thread(target = TeamListApp.Handlers.WebSocketServer.openSocket).start()
except Exception as e:
    print('Error:')
    print(e)
