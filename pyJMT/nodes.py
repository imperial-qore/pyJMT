class Queue:
    def __init__(self, model, name, strategy, capacity=-1):
        self.model = model
        self.name = name
        self.strategy = strategy
        self.services = {}
        self.routings = {}
        self.model.add_queue(self)
        self.numberOfServers = 1
        self.capacity = capacity

    def setService(self, jobclass, service_dist):
        self.services[jobclass.name] = service_dist

    def setNumberOfServers(self, x):
        self.numberOfServers = x


class Delay:
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.services = {}
        self.routings = {}
        self.model.add_delay(self)
        self.numMachines = 1

    def setService(self, jobclass, service):
        self.services[jobclass.name] = service


class Source:
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.routings = {}
        self.services = {}
        self.model.add_source(self)

    def setArrival(self, jobclass, arrival_dist):
        self.services[jobclass.name] = arrival_dist
        jobclass.referenceSource = self.name


class Sink:
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.model.add_sink(self)

class Router:
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.routings = {}
        self.model.add_router(self)

    def setRouting(self, jobclass, routing_strategy):
        self.routings[jobclass.name] = routing_strategy

