import os

from pyJMT.scheduling_strategies import SchedStrategy
from pyJMT.routing_strategies import RoutingStrategy
from itertools import product
from pyJMT.drop_strategies import DropStrategy


class Node:
    def __init__(self, model, name):
        self.model = model
        self.name = name


class QueueSection:

    def __init__(self, strategy, capacity=-1, dropRule=DropStrategy.DROP):
        self.strategy = strategy
        self.capacity = capacity
        self.dropRule = dropRule

    def setStrategy(self, strategy):
        """
                Sets the scheduling strategy for the queue.

                :param strategy: The scheduling strategy.
                :type strategy: SchedStrategy
                """
        self.strategy = strategy

    def setCapacity(self, capacity):
        """
                Sets the capacity for the queue.

                :param capacity: The capacity.
                :type capacity: int
                """
        self.capacity = capacity

    def setDropRule(self, dropRule):
        """
                Sets the drop rule for the queue.

                :param dropRule: The drop rule.
                :type dropRule: DropStrategy
                """
        self.dropRule = dropRule


class ServiceSection:

    def __init__(self, numberOfServers=1):
        self.services = {}
        self.numberOfServers = numberOfServers

    def setService(self, jobclass, service_dist, weight=1.0):
        """
               Sets the service strategy for a given job class.

               :param jobclass: The job class.
               :type jobclass: JobClass
               :param service_dist: The service distribution.
               :type service_dist: Distribution
               :param weight: The weight, defaults to 1.0.
               :type weight: float, optional
               """
        self.services[jobclass.name] = {}
        self.services[jobclass.name]['service_strategy'] = service_dist
        self.services[jobclass.name]['weight'] = weight
        if jobclass.name not in self.routings:
            self.setRouting(jobclass, RoutingStrategy.RANDOM)

    def setNumberOfServers(self, x):
        """
                Sets the number of servers.

                :param x: The number of servers.
                :type x: int
                """
        self.numberOfServers = x


class RoutingSection:

    def __init__(self):
        self.routings = {}

    def setRouting(self, jobclass, routing_strat):
        """
                Sets the routing strategy for a given job class.

                :param jobclass: The job class.
                :type jobclass: JobClass
                :param routing_strat: The routing strategy.
                :type routing_strat: pyJMT.RoutingStrategy
                """
        self.routings[jobclass.name] = {}
        self.routings[jobclass.name]['routing_strat'] = routing_strat
        self.routings[jobclass.name]['probabilities'] = []
        self.routings[jobclass.name]['classswitchprobs'] = {}

    def setProbRouting(self, jobclass, target, val):
        """
                Sets the probability routing for a given job class.

                :param jobclass: The job class.
                :type jobclass: JobClass
                :param target: The target node.
                :type target: Node
                :param val: The routing probability.
                :type val: float
                """
        self.routings[jobclass.name]['probabilities'].append((target.name, val))

    def setClassSwitchRouting(self, sourcejobclass, targetjobclass, target, routeprob, classchangeprob):
        """
               Sets the class switch routing for a source job class to a target job class.

               :param sourcejobclass: The source job class.
               :type sourcejobclass: JobClass
               :param targetjobclass: The target job class.
               :type targetjobclass: JobClass
               :param target: The target node.
               :type target: Node
               :param routeprob: The routing probability.
               :type routeprob: float
               :param classchangeprob: The class change probability.
               :type classchangeprob: float
               """
        if self.routings[sourcejobclass.name]['classswitchprobs'].get((target.name, routeprob), None) is None:
            self.routings[sourcejobclass.name]['classswitchprobs'][(target.name, routeprob)] = {}
        self.routings[sourcejobclass.name]['classswitchprobs'][(target.name, routeprob)][
            targetjobclass] = classchangeprob


class ClassSwitchSection:

    def __init__(self, model):
        self.p = {}
        classes = model.get_classes()
        #TODO THIS WILL LIKELY NOT WORK AS INTENDED WHEN REASSIGNED
        for jclass in classes:
            self.p[jclass.name] = {}
        for c1, c2 in product(classes, repeat=2):
            if c1 == c2:
                self.p[c1.name][c2.name] = 1.0
            else:
                self.p[c1.name][c2.name] = 0.0

    def setClassSwitchProb(self, class1, class2, p):
        """
                Sets the class switch probability from one class to another.

                :param class1: The source job class.
                :type class1: JobClass
                :param class2: The target job class.
                :type class2: JobClass
                :param p: The class switch probability.
                :type p: float
                """
        self.p[class1.name][class2.name] = p


class Queue(Node, QueueSection, ServiceSection, RoutingSection):
    """
      Defines a Queue node in the model.

      :param model: The model in which this node belongs.
      :type model: Network
      :param name: The name of the node.
      :type name: str
      :param strategy: The scheduling strategy used by the queue.
      :type strategy: SchedStrategy
      :param capacity: The maximum capacity of the queue, defaults to -1 for infinite capacity.
      :type capacity: int, optional
      :param dropRule: The rule for dropping jobs when the queue is full, defaults to DropStrategy.DROP.
      :type dropRule: DropStrategy, optional
      """
    def __init__(self, model, name, strategy, capacity=-1, dropRule=DropStrategy.DROP):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        ServiceSection.__init__(self, )
        QueueSection.__init__(self, strategy, capacity, dropRule)
        self.model.nodes["queues"].append(self)


class Delay(Node, RoutingSection, ServiceSection):
    """
        Defines a Delay node in the model.

        :param model: The model in which this node belongs.
        :type model: Network
        :param name: The name of the node.
        :type name: str
        """
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        ServiceSection.__init__(self)
        self.model.nodes["delays"].append(self)


class Source(Node, RoutingSection):
    """
        Defines a Source node in the model.

        :param model: The model in which this node belongs.
        :type model: Network
        :param name: The name of the node.
        :type name: str
        """
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        self.services = {}
        self.model.nodes["sources"].append(self)

    def setArrival(self, jobclass, arrival_dist):
        """
         Sets the arrival distribution for a given job class.

         :param jobclass: The job class.
         :type jobclass: JobClass
         :param arrival_dist: The arrival distribution.
         :type arrival_dist: Distribution
         """
        self.services[jobclass.name] = {}
        self.services[jobclass.name]["service_strategy"] = arrival_dist
        jobclass.referenceSource = self.name
        if jobclass.name not in self.routings:
            self.setRouting(jobclass, RoutingStrategy.RANDOM)


class Sink(Node):
    """
        Defines a Sink node in the model.

        :param model: The model in which this node belongs.
        :type model: Network
        :param name: The name of the node.
        :type name: str
        """
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        self.model.nodes["sinks"].append(self)


class Router(Node, RoutingSection):
    """
       Defines a Router node in the model.

       :param model: The model in which this node belongs.
       :type model: Network
       :param name: The name of the node.
       :type name: str
       """
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        self.model.nodes["routers"].append(self)


class ClassSwitch(Node, RoutingSection, ClassSwitchSection):
    """
       Defines a ClassSwitch node in the model.

       :param model: The model in which this node belongs.
       :type model: Network
       :param name: The name of the node.
       :type name: str
       """
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        ClassSwitchSection.__init__(self, model)
        self.model.nodes["classswitches"].append(self)


class Fork(Node, RoutingSection, QueueSection):
    """
       Defines a Fork node in the model.

       :param model: The model in which this node belongs.
       :type model: Network
       :param name: The name of the node.
       :type name: str
       """
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        QueueSection.__init__(self, SchedStrategy.FCFS)
        self.model.nodes["forks"].append(self)
        self.num_tasks = 1
        self.links = []

    def setTasksPerLink(self, num_tasks):
        """
              Sets the number of tasks per link.

              :param num_tasks: The number of tasks to be split into for each link.
              :type num_tasks: int
              """
        self.num_tasks = num_tasks


class Join(Node, RoutingSection):
    """
        Defines a Join node in the model.

        :param model: The model in which this node belongs.
        :type model: Network
        :param name: The name of the node.
        :type name: str
        """
    def __init__(self, model, name):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        self.model.nodes["joins"].append(self)


class Logger(Node, RoutingSection):
    """
        Defines a Logger node in the model.

        :param model: The model in which this node belongs.
        :type model: Network
        :param name: The name of the node.
        :type name: str
        :param logfileName: The name of the log file, defaults to 'global.csv'.
        :type logfileName: str, optional
        :param logfilePath: The path to the log file, defaults to the directory of JMT.jar.
        :type logfilePath: str, optional
        """
    #TODO CHANGE DEFAULT PATH TO JMT PATH
    def __init__(self, model, name, logfileName="global.csv", logfilePath=os.getcwd()):
        Node.__init__(self, model, name)
        RoutingSection.__init__(self)
        self.logfileName = logfileName
        self.logfilePath = logfilePath
        self.timestamp = True
        self.logLoggerName = True
        self.startTime = False
        self.jobID = True
        self.jobclass = False
        self.timeSameClass = False
        self.timeAnyClass = False
        self.model.nodes["loggers"].append(self)

    def setDelimiter(self, delimiter):
        """
               Sets the delimiter for the log file.

               :param delimiter: The delimiter.
               :type delimiter: str
               """
        self.model.logDelimiter = delimiter

    def setLogLoggerName(self, bool):
        """
               Toggles logging of the logger name.

               :param bool: If true, the logger name will be logged.
               :type bool: bool
               """
        self.logLoggerName = bool

    def setStartTime(self, bool):
        """
               Toggles logging of the start time.

               :param bool: If true, the start time will be logged.
               :type bool: bool
               """
        self.startTime = bool

    def setJobID(self, bool):
        """
              Toggles logging of the job ID.

              :param bool: If true, the job ID will be logged.
              :type bool: bool
              """
        self.jobID = bool

    def setJobClass(self, bool):
        """
            Toggles logging of the job class.

            :param bool: If true, the job class will be logged.
            :type bool: bool
            """
        self.jobclass = bool

    def setTimestamp(self, bool):
        """
              Toggles logging of the timestamp.

              :param bool: If true, the timestamp will be logged.
              :type bool: bool
              """
        self.timestamp = bool

    def setTimeSameClass(self, bool):
        """
             Toggles logging of the time in the same job class.

             :param bool: If true, the time in the same job class will be logged.
             :type bool: bool
             """
        self.timeSameClass = bool

    def setTimeAnyClass(self, bool):
        """
          Toggles logging of the time in any job class.

          :param bool: If true, the time in any job class will be logged.
          :type bool: bool
          """
        self.timeAnyClass = bool

class FiniteCapacityRegion(Node):
    """
        Defines a FiniteCapacityRegion node in the model.

        :param model: The model in which this node belongs.
        :type model: Network
        :param name: The name of the node.
        :type name: str
        :param node: The node associated with this finite capacity region.
        :type node: Node
        :param maxCapacity: The maximum capacity of the region, defaults to -1 for infinite capacity.
        :type maxCapacity: int, optional
        :param maxMemory: The maximum memory of the region, defaults to -1 for infinite memory.
        :type maxMemory: int, optional
        """
    def __init__(self, model, name, node, maxCapacity=-1, maxMemory=-1):
        Node.__init__(self, model, name)
        self.nodeName = node.name
        self.maxCapacity = maxCapacity
        self.maxMemory = maxMemory
        self.classMaxCapacities = {}
        self.classMaxMemories = {}
        self.dropRules = {}
        self.classWeights = {}
        self.classSizes = {}
        self.model.nodes["fcrs"].append(self)


    def setMaxCapacity(self, maxCapacity):
        """
            Sets the maximum capacity of the region.

            :param maxCapacity: The maximum capacity.
            :type maxCapacity: int
            """
        self.maxCapacity = maxCapacity

    def setMaxMemory(self, maxMemory):
        """
           Sets the maximum memory of the region.

           :param maxMemory: The maximum memory.
           :type maxMemory: int
           """
        self.maxMemory = maxMemory

    def setClassMaxCapacity(self, jobclass, maxCapacity):
        """
               Sets the maximum capacity for a given job class.

               :param jobclass: Instance of the job class.
               :type jobclass: JobClass
               :param maxCapacity: Maximum capacity for the job class.
               :type maxCapacity: int
               """
        self.classMaxCapacities[jobclass.name] = maxCapacity

    def setClassMaxMemory(self, jobclass, maxMemory):
        """
              Sets the maximum memory for a given job class.

              :param jobclass: Instance of the job class.
              :type jobclass: JobClass
              :param maxMemory: Maximum memory for the job class.
              :type maxMemory: int
              """
        self.classMaxMemories[jobclass.name] = maxMemory

    def setDropRule(self, jobclass, drop):
        """
            Sets the drop rule for a given job class.

            :param jobclass: Instance of the job class.
            :type jobclass: JobClass
            :param drop: Drop rule for the job class.
            :type drop: JobClass
            """
        self.dropRules[jobclass.name] = drop

    def setClassWeight(self, jobclass, weight):
        """
           Sets the weight for a given job class.

           :param jobclass: Instance of the job class.
           :type jobclass: JobClass
           :param weight: Weight for the job class.
           :type weight: float or int
           """
        self.classWeights[jobclass.name] = weight

    def setClassSize(self, jobclass, size):
        """
            Sets the size for a given job class.

            :param jobclass: Instance of the job class.
            :type jobclass: JobClass
            :param size: Size for the job class.
            :type size: int
            """
        self.classSizes[jobclass.name] = size
