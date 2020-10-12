class DataInstance:
    def __init__(self, dataName, mov_dir, job_inst_idx, total_size, data_inst_idx):
        self.dataName = dataName
        self.mov_dir = mov_dir
        self.job_inst_idx = job_inst_idx
        self.total_size = total_size
        self.data_inst_idx = data_inst_idx
        self.refCnt = 0