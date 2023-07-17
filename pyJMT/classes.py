class OpenClass:
    def __init__(self, model, name, priority=0):
        self.model = model
        self.name = name
        self.model.add_class(self)
        self.referenceSource = None
        self.priority = priority


class ClosedClass:
    def __init__(self, model, name, numMachines, delay, priority=0):
        self.model = model
        self.name = name
        self.model.add_class(self)
        self.referenceSource = delay.name
        self.delay = delay
        self.numMachines = numMachines
        delay.numMachines = numMachines
        self.priority = priority

