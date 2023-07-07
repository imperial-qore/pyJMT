import xml.etree.ElementTree as ET
from enum import Enum

class Network:
    def __init__(self, name):
        self.name = name
        self.sources = []
        self.sinks = []
        self.queues = []
        self.links = []
        self.classes = []

    def add_class(self, oclass):
        self.classes.append(oclass)

    def add_source(self, source):
        self.sources.append(source)

    def add_sink(self, sink):
        self.sinks.append(sink)

    def add_queue(self, queue):
        self.queues.append(queue)

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
                                    "name": "mm1simple.jsimg",
                                    "polling": "1.0",
                                    "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation": "SIMmodeldefinition.xsd"})

        for oclass in self.classes:
            ET.SubElement(sim, "userClass", name=oclass.name, priority="0", referenceSource="mySource", type="open")

        for source in self.sources:
            for oclass, arrival in source.arrivals.items():
                node = ET.SubElement(sim, "node", name=source.name)
                section = ET.SubElement(node, "section", className="RandomSource")
                parameter = ET.SubElement(section, "parameter", array="true",
                                          classPath="jmt.engine.NetStrategies.ServiceStrategy", name="ServiceStrategy")
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
                ET.SubElement(parameter, "refClass").text = oclass
                ET.SubElement(parameter, "subParameter",
                              classPath="jmt.engine.NetStrategies.RoutingStrategies.RoundRobinStrategy",
                              name="Round Robin")

        for sink in self.sinks:
            node = ET.SubElement(sim, "node", name=sink.name)
            ET.SubElement(node, "section", className="JobSink")

        for queue in self.queues:
            for oclass, service in queue.services.items():
                node = ET.SubElement(sim, "node", name=queue.name)
                section = ET.SubElement(node, "section", className="Queue")
                sizepar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="size")
                ET.SubElement(sizepar, "value").text = "-1"

                dropStrategies = ET.SubElement(section, "parameter", array="true", classPath="java.lang.String",
                                               name="dropStrategies")
                ET.SubElement(dropStrategies, "refClass").text = oclass
                dropStrategy = ET.SubElement(dropStrategies, "subParameter", classPath="java.lang.String",
                                             name="dropStrategy")
                ET.SubElement(dropStrategy, "value").text = "drop"
                ET.SubElement(section, "parameter",
                              classPath="jmt.engine.NetStrategies.QueueGetStrategies.FCFSstrategy", name="FCFSstrategy")
                parameter = ET.SubElement(section, "parameter", array="true",
                                          classPath="jmt.engine.NetStrategies.QueuePutStrategy",
                                          name="QueuePutStrategy")
                ET.SubElement(parameter, "refClass").text = oclass
                ET.SubElement(parameter, "subParameter",
                              classPath="jmt.engine.NetStrategies.QueuePutStrategies.TailStrategy", name="TailStrategy")
                section = ET.SubElement(node, "section", className="Server")
                maxJobsPar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="maxJobs")
                ET.SubElement(maxJobsPar, "value").text = "1"

                parameter = ET.SubElement(section, "parameter", array="true", classPath="java.lang.Integer",
                                          name="numberOfVisits")
                ET.SubElement(parameter, "refClass").text = oclass
                numberOfVisits = ET.SubElement(parameter, "subParameter", classPath="java.lang.Integer",
                                               name="numberOfVisits")
                ET.SubElement(numberOfVisits, "value").text = "1"
                parameter = ET.SubElement(section, "parameter", array="true",
                                          classPath="jmt.engine.NetStrategies.ServiceStrategy", name="ServiceStrategy")
                ET.SubElement(parameter, "refClass").text = oclass
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.ServiceStrategies.ServiceTimeStrategy",
                                             name="ServiceTimeStrategy")
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Exponential",
                              name="Exponential")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ExponentialPar",
                                         name="distrPar")
                lambdaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda")
                ET.SubElement(lambdaPar, "value").text = str(float(service.lambda_value))
                section = ET.SubElement(node, "section", className="Router")
                parameter = ET.SubElement(section, "parameter", array="true",
                                          classPath="jmt.engine.NetStrategies.RoutingStrategy", name="RoutingStrategy")
                ET.SubElement(parameter, "refClass").text = oclass
                ET.SubElement(parameter, "subParameter",
                              classPath="jmt.engine.NetStrategies.RoutingStrategies.RandomStrategy", name="Random")

        for link in self.links:
            ET.SubElement(sim, "connection", source=link.source.name, target=link.target.name)

        tree = ET.ElementTree(root)
        with open(fileName, 'wb') as f:
            tree.write(f, encoding='ISO-8859-1', xml_declaration=True)

        tree.write(fileName)


class SchedStrategy(Enum):
    FCFS = "FCFS"
    # Add other scheduling strategies here as needed

class Exponential:
    def __init__(self, lambda_value):
        self.lambda_value = lambda_value

class Link:
    def __init__(self, source, target):
        self.source = source
        self.target = target

class OpenClass:
    def __init__(self, model: Network, name):
        self.model = model
        self.name = name
        self.model.add_class(self)

class Queue:
    def __init__(self, model: Network, name, strategy):
        self.model = model
        self.name = name
        self.strategy = strategy
        self.services = {}
        self.model.add_queue(self)

    def setService(self, oclass, service):
        self.services[oclass.name] = service

class Source:
    def __init__(self, model: Network, name):
        self.model = model
        self.name = name
        self.arrivals = {}
        self.model.add_source(self)


    def setArrival(self, oclass, arrival):
        self.arrivals[oclass.name] = arrival

class Sink:
    def __init__(self, model: Network, name):
        self.model = model
        self.name = name
        self.model.add_sink(self)





