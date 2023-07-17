import pyJMT

from pyJMT.routing_strategies import RoutingStrategy


class Node:
    def __init__(self, model, name):
        self.model = model
        self.name = name


class QueueSection:
    def __init__(self, strategy, capacity=-1):
        self.strategy = strategy
        self.capacity = capacity


class ServiceSection:
    def __init__(self, numberOfServers=1):
        self.services = {}
        self.numberOfServers = numberOfServers

    def setService(self, jobclass, service_dist, weight=1.0):
        self.services[jobclass.name] = {}
        self.services[jobclass.name]['service_strategy'] = service_dist
        self.services[jobclass.name]['weight'] = weight
        if jobclass.name not in self.routings:
            self.setRouting(jobclass, RoutingStrategy.RANDOM)

    def setNumberOfServers(self, x):
        self.numberOfServers = x


class RoutingSection:
    def __init__(self):
        self.routings = {}

    def setRouting(self, jobclass, routing_strat):
        self.routings[jobclass.name] = {}
        self.routings[jobclass.name]['routing_strat'] = routing_strat
        self.routings[jobclass.name]['probabilities'] = {}


class Queue(Node, QueueSection, ServiceSection, RoutingSection):
    def __init__(self, model, name, strategy, capacity=-1):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        ServiceSection.__init__(self,)
        QueueSection.__init__(self, strategy, capacity)
        self.model.add_queue(self)


class Delay(Node, RoutingSection, ServiceSection):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        ServiceSection.__init__(self)
        self.model.add_delay(self)


class Source(Node, RoutingSection):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        self.services = {}
        self.model.add_source(self)

    def setArrival(self, jobclass, arrival_dist):
        self.services[jobclass.name] = {}
        self.services[jobclass.name]["service_strategy"] = arrival_dist
        jobclass.referenceSource = self.name
        if jobclass.name not in self.routings:
            self.setRouting(jobclass, RoutingStrategy.RANDOM)


class Sink(Node):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        self.model.add_sink(self)


class Router(Node, RoutingSection):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        self.model.add_router(self)
