class Queue:
    def __init__(self, model, name, strategy):
        self.model = model
        self.name = name
        self.strategy = strategy
        self.services = {}
        self.model.add_queue(self)
        self.numberOfServers = 1

    def setService(self, oclass, service):
        self.services[oclass.name] = service

    def setNumberOfServers(self, x):
        self.numberOfServers = x


class Delay:
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.services = {}
        self.model.add_delay(self)
        self.numMachines = 1

    def setService(self, jobclass, service):
        self.services[jobclass.name] = service


class Source:
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.arrivals = {}
        self.model.add_source(self)

    def setArrival(self, oclass, arrival):
        self.arrivals[oclass.name] = arrival
        oclass.referenceSource = self.name


class Sink:
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.model.add_sink(self)
