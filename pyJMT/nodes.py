import pyJMT

from pyJMT.routing_strategies import RoutingStrategy
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

    def setService(self, jobclass, service_dist, weight=1.0):
        self.services[jobclass.name] = {}
        self.services[jobclass.name]['service_strategy'] = service_dist
        self.services[jobclass.name]['weight'] = weight
        if jobclass.name not in self.routings:
            self.setRouting(jobclass, RoutingStrategy.RANDOM)

    def setRouting(self, jobclass, routing_strat):
        self.routings[jobclass.name] = {}
        self.routings[jobclass.name]['routing_strat'] = routing_strat
        self.routings[jobclass.name]['probabilities'] = {}

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

    def setService(self, jobclass, service_dist, weight=1.0):
        self.services[jobclass.name] = {}
        self.services[jobclass.name]['service_strategy'] = service_dist
        self.services[jobclass.name]['weight'] = weight
        if jobclass.name not in self.routings:
            self.setRouting(jobclass, RoutingStrategy.RANDOM)

    def setRouting(self, jobclass, routing_strat):
        self.routings[jobclass.name] = {}
        self.routings[jobclass.name]['routing_strat'] = routing_strat
        self.routings[jobclass.name]['probabilities'] = {}

class Source:
    def __init__(self, model, name):
        self.model = model
        self.name = name
        self.routings = {}
        self.services = {}
        self.model.add_source(self)

    def setArrival(self, jobclass, arrival_dist):
        self.services[jobclass.name] = {}
        self.services[jobclass.name]["service_strategy"] = arrival_dist
        jobclass.referenceSource = self.name
        if jobclass.name not in self.routings:
            self.setRouting(jobclass, RoutingStrategy.RANDOM)

    def setRouting(self, jobclass, routing_strat):
        self.routings[jobclass.name] = {}
        self.routings[jobclass.name]['routing_strat'] = routing_strat
        self.routings[jobclass.name]['probabilities'] = {}


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

    def setRouting(self, jobclass, routing_strat):
        self.routings[jobclass.name] = {}
        self.routings[jobclass.name]['routing_strat'] = routing_strat
        self.routings[jobclass.name]['probabilities'] = {}

