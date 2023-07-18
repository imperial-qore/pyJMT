from pyJMT.scheduling_strategies import SchedStrategy
from pyJMT.routing_strategies import RoutingStrategy
from itertools import product


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
        self.routings[jobclass.name]['probabilities'] = []

    def setProbRouting(self, jobclass, target, val):
        self.routings[jobclass.name]['probabilities'].append((target.name, val))


class ClassSwitchSection:
    def __init__(self, model):
        self.p = {}
        classes = model.get_classes()
        for jclass in classes:
            self.p[jclass.name] = {}
        for c1, c2 in product(classes, repeat=2):
            if c1 == c2:
                self.p[c1.name][c2.name] = 1.0
            else:
                self.p[c1.name][c2.name] = 0.0

    def setClassSwitchProb(self, class1, class2, p):
        self.p[class1.name][class2.name] = p


class Queue(Node, QueueSection, ServiceSection, RoutingSection):
    def __init__(self, model, name, strategy, capacity=-1):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        ServiceSection.__init__(self, )
        QueueSection.__init__(self, strategy, capacity)
        self.model.nodes["queues"].append(self)


class Delay(Node, RoutingSection, ServiceSection):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        ServiceSection.__init__(self)
        self.model.nodes["delays"].append(self)



class Source(Node, RoutingSection):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        self.services = {}
        self.model.nodes["sources"].append(self)


    def setArrival(self, jobclass, arrival_dist):
        self.services[jobclass.name] = {}
        self.services[jobclass.name]["service_strategy"] = arrival_dist
        jobclass.referenceSource = self.name
        if jobclass.name not in self.routings:
            self.setRouting(jobclass, RoutingStrategy.RANDOM)


class Sink(Node):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        self.model.nodes["sinks"].append(self)


class Router(Node, RoutingSection):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        self.model.nodes["routers"].append(self)


class ClassSwitch(Node, RoutingSection, ClassSwitchSection):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        ClassSwitchSection.__init__(self, model)
        self.model.nodes["classswitches"].append(self)

class Fork(Node, RoutingSection, QueueSection):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        QueueSection.__init__(self, SchedStrategy.FCFS)
        self.model.nodes["forks"].append(self)
        self.num_tasks = 1
        self.links = []

    def setTasksPerLink(self, num_tasks):
        self.num_tasks = num_tasks

class Join(Node, RoutingSection):
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        self.model.nodes["joins"].append(self)
