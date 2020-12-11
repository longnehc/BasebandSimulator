class DataInstance:
    def __init__(self, dataName, mov_dir, job_inst_idx, total_size, data_inst_idx):
        self.dataName = dataName
        self.mov_dir = mov_dir
        self.job_inst_idx = job_inst_idx
        self.total_size = total_size
        self.data_inst_idx = data_inst_idx
        self.remain_time = 0

    def __hash__(self):
        return hash(self.dataName)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.data_inst_idx == other.data_inst_idx and self.dataName == other.dataName
        else:
            return False