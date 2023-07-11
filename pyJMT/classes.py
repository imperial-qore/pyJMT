class OpenClass:
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.model.add_openclass(self)
        self.referenceSource = None


class ClosedClass:
    def __init__(self, model, name, numMachines, delay):
        self.model = model
        self.name = name
        self.model.add_closedclass(self)
        self.referenceSource = delay.name
        self.delay = delay
        self.numMachines = numMachines
        delay.numMachines = numMachines
