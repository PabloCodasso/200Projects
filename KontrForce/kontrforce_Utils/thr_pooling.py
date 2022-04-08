from concurrent.futures import ThreadPoolExecutor

class Pooler():
    def __init__(self):
        self.cutor = ThreadPoolExecutor(max_workers=1)

    def pooling(self, pool_targ, pool_args):
        self.cutor.submit(pool_targ,pool_args)