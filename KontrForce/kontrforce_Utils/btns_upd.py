
def btn_upd(arg_list):
    print('UPD START')
    arg_list[0].start(5)
    for butn in arg_list[2]:
        butn.get_disabled()
    while True:
        if arg_list[1].recv():
            for butn in arg_list[2]:
                butn.get_enabled()
            arg_list[0].stop()
            break
    arg_list[0] = False
    return
