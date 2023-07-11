import os
import xml.etree.ElementTree as ET
from enum import Enum

class Network:
    def __init__(self, name):
        self.name = name
        self.sources: [Source] = []
        self.sinks: [Sink] = []
        self.queues: [Queue] = []
        self.delays: [Delay] = []
        self.links: [Link] = []
        self.openclasses: [OpenClass] = []
        self.closedclasses: [ClosedClass] = []

    def add_openclass(self, oclass):
        self.openclasses.append(oclass)

    def add_closedclass(self, cclass):
        self.openclasses.append(cclass)

    def add_source(self, source):
        self.sources.append(source)

    def add_sink(self, sink):
        self.sinks.append(sink)

    def add_queue(self, queue):
        self.queues.append(queue)

    def add_delay(self, delay):
        self.delays.append(delay)

    def add_link(self, link):
        self.links.append(link)

    def link(self, source, target):
        link = Link(source, target)
        self.add_link(link)

    def generate_xml(self, fileName):
        ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

        root = ET.Element("archive",
                          attrib={"name": fileName,
                                  "timestamp": "Fri Jul 07 14:27:52 BST 2023",
                                  "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation": "Archive.xsd"})

        sim = ET.SubElement(root, "sim",
                            attrib={"disableStatisticStop": "false",
                                    "logDecimalSeparator": ".",
                                    "logDelimiter": ",",
                                    "logPath": "/home/james/JMT/",
                                    "logReplaceMode": "0",
                                    "maxEvents": "-1",
                                    "maxSamples": "1000000",
                                    "name": fileName,
                                    "polling": "1.0",
                                    "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation": "SIMmodeldefinition.xsd"})

        for oclass in self.openclasses:
            ET.SubElement(sim, "userClass", name=oclass.name, priority="0", referenceSource=oclass.referenceSource, type="open")

        for cclass in self.closedclasses:
            ET.SubElement(sim, "userClass", customers=cclass.numMachines ,name=cclass.name, priority="0", referenceSource=cclass.referenceSource, type="closed")

        for source in self.sources:
            node = ET.SubElement(sim, "node", name=source.name)
            section = ET.SubElement(node, "section", className="RandomSource")
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.ServiceStrategy", name="ServiceStrategy")

            for oclass, arrival in source.arrivals.items():
                ET.SubElement(parameter, "refClass").text = oclass
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.ServiceStrategies.ServiceTimeStrategy",
                                             name="ServiceTimeStrategy")
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Exponential",
                              name="Exponential")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ExponentialPar",
                                         name="distrPar")
                lambdaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda")
                ET.SubElement(lambdaPar, "value").text = str(float(arrival.lambda_value))

            ET.SubElement(node, "section", className="ServiceTunnel")
            section = ET.SubElement(node, "section", className="Router")
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.RoutingStrategy", name="RoutingStrategy")

            for oclass in source.arrivals.keys():
                refClass = ET.SubElement(parameter, "refClass")
                refClass.text = oclass
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.RoutingStrategies.EmpiricalStrategy",
                                             name="Probabilities")
                empiricalEntryArray = ET.SubElement(subParameter, "subParameter", array="true",
                                                    classPath="jmt.engine.random.EmpiricalEntry",
                                                    name="EmpiricalEntryArray")
                empiricalEntry = ET.SubElement(empiricalEntryArray, "subParameter",
                                               classPath="jmt.engine.random.EmpiricalEntry", name="EmpiricalEntry")
                stationName = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.String",
                                            name="stationName")
                target = ""
                for link in self.links:
                    if link.source.name == source.name:
                        target = link.target.name
                        break
                ET.SubElement(stationName, "value").text = target
                probability = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.Double",
                                            name="probability")
                ET.SubElement(probability, "value").text = "1.0"

        for queue in self.queues:
            node = ET.SubElement(sim, "node", name=queue.name)
            section = ET.SubElement(node, "section", className="Queue")
            sizepar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="size")
            ET.SubElement(sizepar, "value").text = "-1"

            dropStrategies = ET.SubElement(section, "parameter", array="true", classPath="java.lang.String",
                                           name="dropStrategies")

            for oclass in queue.services.keys():
                ET.SubElement(dropStrategies, "refClass").text = oclass
                dropStrategy = ET.SubElement(dropStrategies, "subParameter", classPath="java.lang.String",
                                             name="dropStrategy")
                ET.SubElement(dropStrategy, "value").text = "waiting queue"

            ET.SubElement(section, "parameter",
                          classPath="jmt.engine.NetStrategies.QueueGetStrategies.FCFSstrategy", name="FCFSstrategy")
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.QueuePutStrategy",
                                      name="QueuePutStrategy")

            for oclass in queue.services.keys():
                ET.SubElement(parameter, "refClass").text = oclass
                ET.SubElement(parameter, "subParameter",
                              classPath="jmt.engine.NetStrategies.QueuePutStrategies.TailStrategy", name="TailStrategy")

            section = ET.SubElement(node, "section", className="Server")
            maxJobsPar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="maxJobs")
            ET.SubElement(maxJobsPar, "value").text = str(queue.numberOfServers)

            parameter = ET.SubElement(section, "parameter", array="true", classPath="java.lang.Integer",
                                      name="numberOfVisits")
            for oclass in queue.services.keys():
                ET.SubElement(parameter, "refClass").text = oclass
                numberOfVisits = ET.SubElement(parameter, "subParameter", classPath="java.lang.Integer",
                                               name="numberOfVisits")
                ET.SubElement(numberOfVisits, "value").text = "1"

            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.ServiceStrategy", name="ServiceStrategy")
            for oclass, service in queue.services.items():
                ET.SubElement(parameter, "refClass").text = oclass
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.ServiceStrategies.ServiceTimeStrategy",
                                             name="ServiceTimeStrategy")

                if isinstance(service, Exp):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Exponential",
                                  name="Exponential")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ExponentialPar",
                                             name="distrPar")
                    lambdaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda")
                    ET.SubElement(lambdaPar, "value").text = str(float(service.lambda_value))
                elif isinstance(service, Erlang):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Erlang",
                                  name="Erlang")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ErlangPar",
                                             name="distrPar")
                    alphaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                    ET.SubElement(alphaPar, "value").text = str(float(service.alpha))
                    rPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Long", name="r")
                    ET.SubElement(rPar, "value").text = str(int(service.r))
                elif isinstance(service, Replayer):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Replayer",
                                  name="Replayer")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ReplayerPar",
                                             name="distrPar")
                    lambdaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.String", name="fileName")
                    ET.SubElement(lambdaPar, "value").text = service.fileName

            section = ET.SubElement(node, "section", className="Router")
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.RoutingStrategy", name="RoutingStrategy")
            for oclass in queue.services.keys():
                refClass = ET.SubElement(parameter, "refClass")
                refClass.text = oclass
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.RoutingStrategies.EmpiricalStrategy",
                                             name="Probabilities")
                empiricalEntryArray = ET.SubElement(subParameter, "subParameter", array="true",
                                                    classPath="jmt.engine.random.EmpiricalEntry",
                                                    name="EmpiricalEntryArray")
                empiricalEntry = ET.SubElement(empiricalEntryArray, "subParameter",
                                               classPath="jmt.engine.random.EmpiricalEntry", name="EmpiricalEntry")
                stationName = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.String",
                                            name="stationName")
                target = ""
                for link in self.links:
                    if link.source.name == queue.name:
                        target = link.target.name
                        break
                ET.SubElement(stationName, "value").text = target
                probability = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.Double",
                                            name="probability")
                ET.SubElement(probability, "value").text = "1.0"

        for delay in self.delays:
            node = ET.SubElement(sim, "node", name=delay.name)
            section = ET.SubElement(node, "section", className="Queue")
            sizepar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="size")
            ET.SubElement(sizepar, "value").text = "-1"

            dropStrategies = ET.SubElement(section, "parameter", array="true", classPath="java.lang.String",
                                           name="dropStrategies")

            for cclass in delay.services.keys():
                ET.SubElement(dropStrategies, "refClass").text = cclass
                dropStrategy = ET.SubElement(dropStrategies, "subParameter", classPath="java.lang.String",
                                             name="dropStrategy")
                ET.SubElement(dropStrategy, "value").text = "drop"

            ET.SubElement(section, "parameter",
                          classPath="jmt.engine.NetStrategies.QueueGetStrategies.FCFSstrategy", name="FCFSstrategy")
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.QueuePutStrategy",
                                      name="QueuePutStrategy")

            for cclass in delay.services.keys():
                ET.SubElement(parameter, "refClass").text = cclass
                ET.SubElement(parameter, "subParameter",
                              classPath="jmt.engine.NetStrategies.QueuePutStrategies.TailStrategy", name="TailStrategy")

            section = ET.SubElement(node, "section", className="Delay")
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.ServiceStrategy", name="ServiceStrategy")
            for jobclass, service in delay.services.items():
                ET.SubElement(parameter, "refClass").text = jobclass
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.ServiceStrategies.ServiceTimeStrategy",
                                             name="ServiceTimeStrategy")

                if isinstance(service, Exp):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Exponential",
                                  name="Exponential")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ExponentialPar",
                                             name="distrPar")
                    lambdaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda")
                    ET.SubElement(lambdaPar, "value").text = str(float(service.lambda_value))
                elif isinstance(service, Erlang):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Erlang",
                                  name="Erlang")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ErlangPar",
                                             name="distrPar")
                    alphaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                    ET.SubElement(alphaPar, "value").text = str(float(service.alpha))
                    rPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Long", name="r")
                    ET.SubElement(rPar, "value").text = str(int(service.r))
                elif isinstance(service, Replayer):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Replayer",
                                  name="Replayer")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ReplayerPar",
                                             name="distrPar")
                    lambdaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.String", name="fileName")
                    ET.SubElement(lambdaPar, "value").text = service.fileName


            section = ET.SubElement(node, "section", className="Router")
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.RoutingStrategy", name="RoutingStrategy")
            for oclass in delay.services.keys():
                refClass = ET.SubElement(parameter, "refClass")
                refClass.text = oclass
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.RoutingStrategies.EmpiricalStrategy",
                                             name="Probabilities")
                empiricalEntryArray = ET.SubElement(subParameter, "subParameter", array="true",
                                                    classPath="jmt.engine.random.EmpiricalEntry",
                                                    name="EmpiricalEntryArray")
                empiricalEntry = ET.SubElement(empiricalEntryArray, "subParameter",
                                               classPath="jmt.engine.random.EmpiricalEntry", name="EmpiricalEntry")
                stationName = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.String",
                                            name="stationName")
                target = ""
                for link in self.links:
                    if link.source.name == delay.name:
                        target = link.target.name
                        break
                ET.SubElement(stationName, "value").text = target
                probability = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.Double",
                                            name="probability")
                ET.SubElement(probability, "value").text = "1.0"

        for sink in self.sinks:
            node = ET.SubElement(sim, "node", name=sink.name)
            ET.SubElement(node, "section", className="JobSink")

        measuresQueue = ["Number of Customers", "Utilization", "Response Time", "Throughput", "Arrival Rate"]
        for measure in measuresQueue:
            for queue in self.queues:
                for oclass in queue.services.keys():
                    ET.SubElement(sim, "measure", alpha="0.01", name=f"{queue.name}_{oclass}_{measure}", nodeType="station",
                                  precision="0.03", referenceNode=queue.name, referenceUserClass=f"{oclass}", type=measure,
                                  verbose="false")

        measuresDelay = ["Number of Customers", "Utilization", "Response Time", "Throughput", "Arrival Rate"]
        for measure in measuresDelay:
            for delay in self.delays:
                for jobclass in delay.services.keys():
                    ET.SubElement(sim, "measure", alpha="0.01", name=f"{delay.name}_{jobclass}_{measure}",
                                  nodeType="station",
                                  precision="0.03", referenceNode=delay.name, referenceUserClass=f"{jobclass}",
                                  type=measure,
                                  verbose="false")

        measuresSource = ["Throughput", "Arrival Rate"]
        for measure in measuresSource:
            for source in self.sources:
                for oclass in source.arrivals.keys():
                    ET.SubElement(sim, "measure", alpha="0.01", name=f"{source.name}_{oclass}_{measure}", nodeType="station",
                                  precision="0.03", referenceNode=source.name, referenceUserClass=f"{oclass}", type=measure,
                                  verbose="false")


        for link in self.links:
            ET.SubElement(sim, "connection", source=link.source.name, target=link.target.name)


        for delay in self.delays:
            preload = ET.SubElement(sim, "preload")
            stationPopulations = ET.SubElement(preload, "stationPopulations", stationName=delay.name)
            ET.SubElement(stationPopulations, "classPopulation", population=str(delay.numMachines), refClass=delay.name)


        tree = ET.ElementTree(root)
        with open(fileName, 'wb') as f:
            tree.write(f, encoding='ISO-8859-1', xml_declaration=True)

        tree.write(fileName)


class SchedStrategy(Enum):
    FCFS = "FCFS"
    # Add other scheduling strategies here as needed

class Exp:
    def __init__(self, lambda_value):
        self.lambda_value = lambda_value


class Erlang:
    def __init__(self, alpha, r):
        self.alpha = alpha
        self.r = r

    @staticmethod
    def fitMeanAndSCV(mean, scv):
        r = 1/scv
        alpha = r/mean
        return Erlang(alpha, r)

class Replayer:
    def __init__(self, fileName):
        self.fileName = os.getcwd() + "/" + fileName

class Link:
    def __init__(self, source, target):
        self.source = source
        self.target = target

class OpenClass:
    def __init__(self, model: Network, name):
        self.model = model
        self.name = name
        self.model.add_openclass(self)
        self.referenceSource = None

class ClosedClass:
    def __init__(self, model: Network, name, numMachines, delay):
        self.model = model
        self.name = name
        self.model.add_closedclass(self)
        self.referenceSource = delay.name
        self.delay = delay
        self.numMachines = numMachines
        delay.numMachines = numMachines


class Queue:
    def __init__(self, model: Network, name, strategy):
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
    def __init__(self, model: Network, name):
        self.model = model
        self.name = name
        self.services = {}
        self.model.add_delay(self)
        self.numMachines = 1

    def setService(self, jobclass, service):
        self.services[jobclass.name] = service

class Source:
    def __init__(self, model: Network, name):
        self.model = model
        self.name = name
        self.arrivals = {}
        self.model.add_source(self)


    def setArrival(self, oclass, arrival):
        self.arrivals[oclass.name] = arrival
        oclass.referenceSource = self.name

class Sink:
    def __init__(self, model: Network, name):
        self.model = model
        self.name = name
        self.model.add_sink(self)





