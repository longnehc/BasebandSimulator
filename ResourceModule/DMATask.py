class DMATask:
    def __init__(self, data):
        self.data = data


    def getData(self):
        return self.data

    def __hash__(self):
        return hash(self.data.dataName)

    def __eq__(self, other):
        if not isinstance(other,DMATask):
            return False
        return self.data.dataName == other.data.dataName