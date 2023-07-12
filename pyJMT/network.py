import xml.etree.ElementTree as ET
from .nodes import Source, Sink, Queue, Delay, Router
from .classes import OpenClass, ClosedClass
from .services import Exp, Erlang, Replayer, SchedStrategy, RoutingStrategy
from .link import Link


class Network:
    def __init__(self, name):
        self.name = name
        self.sources: [Source] = []
        self.sinks: [Sink] = []
        self.queues: [Queue] = []
        self.delays: [Delay] = []
        self.links: [Link] = []
        self.routers: [Router] = []
        self.classes = []

    def add_class(self, jobclass):
        self.classes.append(jobclass)

    def add_source(self, source):
        self.sources.append(source)

    def add_sink(self, sink):
        self.sinks.append(sink)

    def add_queue(self, queue):
        self.queues.append(queue)

    def add_delay(self, delay):
        self.delays.append(delay)

    def add_router(self, router):
        self.routers.append(router)

    def add_link(self, link):
        self.links.append(link)

    def link(self, source, target):
        link = Link(source, target)
        self.add_link(link)

    def addLinks(self, linkList):
        for source, target in linkList:
            self.link(source, target)

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

        self.generate_classes(sim)

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

            self.generate_router(source, node)

        for router in self.routers:
            node = ET.SubElement(sim, "node", name=router.name)
            section = ET.SubElement(node, "section", className="Queue")
            sizepar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="size")
            ET.SubElement(sizepar, "value").text = "-1"

            dropStrategies = ET.SubElement(section, "parameter", array="true", classPath="java.lang.String",
                                           name="dropStrategies")

            for jobclass in self.classes:
                ET.SubElement(dropStrategies, "refClass").text = jobclass.name
                dropStrategy = ET.SubElement(dropStrategies, "subParameter", classPath="java.lang.String",
                                             name="dropStrategy")
                ET.SubElement(dropStrategy, "value").text = "drop"

            ET.SubElement(section, "parameter",
                          classPath="jmt.engine.NetStrategies.QueueGetStrategies.FCFSstrategy", name="FCFSstrategy")
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.QueuePutStrategy",
                                      name="QueuePutStrategy")

            for jobclass in self.classes:
                ET.SubElement(parameter, "refClass").text = jobclass.name
                ET.SubElement(parameter, "subParameter",
                              classPath="jmt.engine.NetStrategies.QueuePutStrategies.TailStrategy", name="TailStrategy")

            ET.SubElement(node, "section", className="ServiceTunnel")
            self.generate_router(router, node)

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

            serverclassname = ""
            if(queue.strategy == SchedStrategy.FCFS):
                serverclassname = "Server"
            elif(queue.strategy == SchedStrategy.PS):
                serverclassname = "PSServer"
            section = ET.SubElement(node, "section", className=serverclassname)
            maxJobsPar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="maxJobs")
            ET.SubElement(maxJobsPar, "value").text = str(queue.numberOfServers)

            if(queue.strategy == SchedStrategy.PS):
                maxRunningPar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="maxRunning")
                ET.SubElement(maxRunningPar, "value").text = "-1"
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


            if(queue.strategy == SchedStrategy.PS):
                parameter = ET.SubElement(section, "parameter", array="true",
                                          classPath="jmt.engine.NetStrategies.PSStrategy", name="PSStrategy")
                for oclass, service in queue.services.items():
                    ET.SubElement(parameter, "refClass").text = oclass
                    ET.SubElement(parameter, "subParameter",
                                                 classPath="jmt.engine.NetStrategies.PSStrategies.EPSStrategy",
                                                 name="EPSStrategy")

                parameter = ET.SubElement(section, "parameter", array="true",
                                          classPath="java.lang.Double", name="serviceWeights")
                for oclass, service in queue.services.items():
                    ET.SubElement(parameter, "refClass").text = oclass
                    subParameter = ET.SubElement(parameter, "subParameter",
                                  classPath="java.lang.Double",
                                  name="serviceWeight")
                    ET.SubElement(subParameter, "value").text = "1.0"

            self.generate_router(queue, node)

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

            self.generate_router(delay, node)

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
            for jobclass in delay.services.keys():
                ET.SubElement(stationPopulations, "classPopulation", population=str(delay.numMachines),
                              refClass=jobclass)

        tree = ET.ElementTree(root)
        with open(fileName, 'wb') as f:
            tree.write(f, encoding='ISO-8859-1', xml_declaration=True)

        tree.write(fileName)

    def generate_router(self, node, nodeTag):
        section = ET.SubElement(nodeTag, "section", className="Router")
        parameter = ET.SubElement(section, "parameter", array="true",
                                  classPath="jmt.engine.NetStrategies.RoutingStrategy", name="RoutingStrategy")
        for jobclass in self.classes:
            routing = node.routings.get(jobclass.name)
            refClass = ET.SubElement(parameter, "refClass")
            refClass.text = jobclass.name
            if routing == RoutingStrategy.RANDOM or routing is None:
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.RoutingStrategies.RandomStrategy",
                                             name="Random")
            elif routing == RoutingStrategy.RROBIN:
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.RoutingStrategies.RoundRobinStrategy",
                                             name="Round Robin")
            elif routing == RoutingStrategy.PROBABILITIES: #TODO IMPLEMENT THIS PROPERLY
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
                for link in self.links:
                    if link.source.name == node.name:
                        target = link.target.name
                        ET.SubElement(stationName, "value").text = target
                        probability = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.Double",
                                                    name="probability")
                        ET.SubElement(probability, "value").text = "1.0"

    def generate_classes(self, simTag):
        for jobclass in self.classes:
            if isinstance(jobclass, OpenClass):
                ET.SubElement(simTag, "userClass", name=jobclass.name, priority="0",
                              referenceSource=jobclass.referenceSource, type="open")

            elif isinstance(jobclass, ClosedClass):
                ET.SubElement(simTag, "userClass", customers=str(jobclass.numMachines), name=jobclass.name, priority="0",
                              referenceSource=jobclass.referenceSource, type="closed")
