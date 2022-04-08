from multiprocessing import Process

def processStart (proc_targ, proc_arg, proc_name):
    prcs = Process(target=proc_targ, args=proc_arg, name=proc_name, daemon=True)
    prcs.start()
    