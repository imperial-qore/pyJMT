import xml.etree.ElementTree as ET
from .nodes import Source, Sink, Queue, Delay, Router
from .classes import OpenClass, ClosedClass
from .services import Exp, Erlang, Replayer, SchedStrategy, RoutingStrategy
from .link import Link
import os
import subprocess


class Network:
    def __init__(self, name):
        self.name = name

        self.nodes = {}
        self.nodes['sources']: [Source] = []
        self.nodes['sinks']: [Sink] = []
        self.nodes['queues']: [Queue] = []
        self.nodes['delays']: [Delay] = []
        self.nodes['routers']: [Router] = []


        self.links: [Link] = []
        self.classes = []

    def get_number_of_nodes(self):
        total_length = sum(len(v) for v in self.nodes.values())
        return total_length

    def get_number_of_classes(self):
        return len(self.classes)

    def get_nodes(self):
        return [value for sublist in self.nodes.values() for value in sublist]

    def get_classes(self):
        return self.classes

    def add_class(self, jobclass):
        self.classes.append(jobclass)

    def add_source(self, source):
        self.nodes['sources'].append(source)

    def add_sink(self, sink):
        self.nodes['sinks'].append(sink)

    def add_queue(self, queue):
        self.nodes['queues'].append(queue)

    def add_delay(self, delay):
        self.nodes['delays'].append(delay)

    def add_router(self, router):
        self.nodes['routers'].append(router)

    def add_link(self, link):
        self.links.append(link)

    def link(self, source, target):
        link = Link(source, target)
        self.add_link(link)

    def addLinks(self, linkList):
        for source, target in linkList:
            self.link(source, target)


    def jsimg_open(self, jmt_path, filename):
        path = os.path.dirname(filename)
        if not path:
            filename = os.path.join(os.getcwd(), filename)
        cmd = f'java -cp "{os.path.join(jmt_path, "JMT.jar")}" jmt.commandline.Jmt jsimg "{filename}"'
        subprocess.run(cmd, shell=True)

    def init_routing_matrix(self):
        nodes = self.get_nodes()
        classes = self.get_classes()
        P = {c1: {c2: {n1: {n2: 0 for n2 in nodes} for n1 in nodes} for c2 in classes} for c1 in classes}
        return P

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

        for source in self.nodes['sources']:
            node = ET.SubElement(sim, "node", name=source.name)

            section = ET.SubElement(node, "section", className="RandomSource")
            self.generate_servicestrategy(source, section)

            ET.SubElement(node, "section", className="ServiceTunnel")

            self.generate_router(source, node)

        for router in self.nodes['routers']:
            node = ET.SubElement(sim, "node", name=router.name)

            self.generate_queuesection(router, node)

            ET.SubElement(node, "section", className="ServiceTunnel")

            self.generate_router(router, node)

        for queue in self.nodes['queues']:
            node = ET.SubElement(sim, "node", name=queue.name)

            self.generate_queuesection(queue, node)

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

            self.generate_servicestrategy(queue, section)


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

        for delay in self.nodes['delays']:
            node = ET.SubElement(sim, "node", name=delay.name)

            self.generate_queuesection(delay, node)

            section = ET.SubElement(node, "section", className="Delay")

            self.generate_servicestrategy(delay, section)

            self.generate_router(delay, node)

        for sink in self.nodes['sinks']:
            node = ET.SubElement(sim, "node", name=sink.name)
            ET.SubElement(node, "section", className="JobSink")

        measuresQueue = ["Number of Customers", "Utilization", "Response Time", "Throughput", "Arrival Rate"]
        for measure in measuresQueue:
            for queue in self.nodes['queues']:
                for oclass in queue.services.keys():
                    ET.SubElement(sim, "measure", alpha="0.01", name=f"{queue.name}_{oclass}_{measure}", nodeType="station",
                                  precision="0.03", referenceNode=queue.name, referenceUserClass=f"{oclass}", type=measure,
                                  verbose="false")

        measuresDelay = ["Number of Customers", "Utilization", "Response Time", "Throughput", "Arrival Rate"]
        for measure in measuresDelay:
            for delay in self.nodes['delays']:
                for jobclass in delay.services.keys():
                    ET.SubElement(sim, "measure", alpha="0.01", name=f"{delay.name}_{jobclass}_{measure}",
                                  nodeType="station",
                                  precision="0.03", referenceNode=delay.name, referenceUserClass=f"{jobclass}",
                                  type=measure,
                                  verbose="false")

        measuresSource = ["Throughput", "Arrival Rate"]
        for measure in measuresSource:
            for source in self.nodes['sources']:
                for oclass in source.services.keys():
                    ET.SubElement(sim, "measure", alpha="0.01", name=f"{source.name}_{oclass}_{measure}", nodeType="station",
                                  precision="0.03", referenceNode=source.name, referenceUserClass=f"{oclass}", type=measure,
                                  verbose="false")

        for link in self.links:
            ET.SubElement(sim, "connection", source=link.source.name, target=link.target.name)

        for delay in self.nodes['delays']:
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

    def generate_servicestrategy(self, node,  parentTag):
        parameter = ET.SubElement(parentTag, "parameter", array="true",
                                  classPath="jmt.engine.NetStrategies.ServiceStrategy", name="ServiceStrategy")
        for jobclass in self.classes:
            service = node.services.get(jobclass.name)

            ET.SubElement(parameter, "refClass").text = jobclass.name
            subParameter = ET.SubElement(parameter, "subParameter",
                                         classPath="jmt.engine.NetStrategies.ServiceStrategies.ServiceTimeStrategy",
                                         name="ServiceTimeStrategy")
            if service is None:
                if isinstance(node, Source):
                    ET.SubElement(subParameter, "value").text="null"
                else:
                    print(f"for {node.name}, {jobclass.name} service distribution not found")

            elif isinstance(service, Exp):
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

    def generate_queuesection(self, node, parentTag):

        section = ET.SubElement(parentTag, "section", className="Queue")
        #TODO ADD DIFFERENT CAPACITIES BASED ON QUEUE
        sizepar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="size")
        ET.SubElement(sizepar, "value").text = "-1"

        dropStrategies = ET.SubElement(section, "parameter", array="true", classPath="java.lang.String",
                                       name="dropStrategies")

        #TODO FIGURE OUT WHAT CAUSES DROP TYPE TO CHANGE
        drop = "drop"
        if isinstance(node, Queue):
            drop = "waiting queue"

        for jobclass in self.classes:
            ET.SubElement(dropStrategies, "refClass").text = jobclass.name
            dropStrategy = ET.SubElement(dropStrategies, "subParameter", classPath="java.lang.String",
                                         name="dropStrategy")
            ET.SubElement(dropStrategy, "value").text = drop

        ET.SubElement(section, "parameter",
                      classPath="jmt.engine.NetStrategies.QueueGetStrategies.FCFSstrategy", name="FCFSstrategy")
        parameter = ET.SubElement(section, "parameter", array="true",
                                  classPath="jmt.engine.NetStrategies.QueuePutStrategy",
                                  name="QueuePutStrategy")

        for jobclass in self.classes:
            ET.SubElement(parameter, "refClass").text = jobclass.name
            ET.SubElement(parameter, "subParameter",
                          classPath="jmt.engine.NetStrategies.QueuePutStrategies.TailStrategy", name="TailStrategy")

