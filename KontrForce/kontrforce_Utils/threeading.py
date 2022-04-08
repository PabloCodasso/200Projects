from threading import Thread

def start_thread (thr_targ, thr_args, thr_name):
    new_thread = Thread(target=thr_targ, args=thr_args, name=thr_name, daemon=True)
    new_thread.start()