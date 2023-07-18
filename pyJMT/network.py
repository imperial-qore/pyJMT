import xml.etree.ElementTree as ET
from .nodes import Source, Sink, Queue, Delay, Router, Fork, Join
from .classes import OpenClass, ClosedClass
from .service_distributions import Cox, Det, Exp, Erlang, Gamma, HyperExp, Lognormal, Normal, Pareto, \
    Replayer, Uniform, Weibull
from .routing_strategies import RoutingStrategy
from .scheduling_strategies import SchedStrategy
from .link import Link
import os
import subprocess
from itertools import product


class Network:
    def __init__(self, name):
        self.name = name
        self.nodes = {'sources': [], 'sinks': [], 'queues': [], 'delays': [],
                      'routers': [], 'classswitches': [], 'forks': [], 'joins': []}
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

    def add_link(self, source, target):
        # Adds links onto fork object to avoid having to search through
        # the links later, this problem only occurs when generating xml
        # for forks
        if isinstance(source, Fork):
            source.links.append(target.name)
        link = Link(source, target)
        self.links.append(link)

    def add_links(self, linkList):
        for source, target in linkList:
            self.add_link(source, target)

    def link(self, p):
        for linkClass, classDict in p:
            if linkClass is tuple:
                #generate classswitch
                c1, c2 = linkClass

            else:
                for (n1, n2) in classDict:
                    containsAlready = False
                    for link in self.links:
                        if link.source == n1 and link.target == n2:
                            containsAlready = True
                            break
                    if containsAlready:
                        break
                    else:
                        self.add_link(n1, n2)

    def jsimg_open(self, jmt_path, filename):
        path = os.path.dirname(filename)
        if not path:
            filename = os.path.join(os.getcwd(), filename)
        cmd = f'java -cp "{os.path.join(jmt_path, "JMT.jar")}" jmt.commandline.Jmt jsimg "{filename}"'
        subprocess.run(cmd, shell=True)

    def init_routing_matrix(self):
        #TODO see if this is ok
        classes = self.get_classes()

        P = {}
        # For P[class_name][node_name][node_name]
        for c in classes:
                P[c] = {}

        # For P[class_name][class_name][node_name][node_name]
        for c1, c2 in product(classes, repeat=2):
            P[(c1, c2)] = {}

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

            self.generate_serversection(queue, node)

            self.generate_router(queue, node)

        for delay in self.nodes['delays']:
            node = ET.SubElement(sim, "node", name=delay.name)

            self.generate_queuesection(delay, node)

            section = ET.SubElement(node, "section", className="Delay")

            self.generate_servicestrategy(delay, section)

            self.generate_router(delay, node)

        for classswitch in self.nodes['classswitches']:
            node = ET.SubElement(sim, "node", name=classswitch.name)
            self.generate_queuesection(classswitch, node)

            self.generate_classswitchsection(classswitch, node)

            self.generate_router(classswitch, node)

        for fork in self.nodes['forks']:
            node = ET.SubElement(sim, "node", name=fork.name)

            self.generate_queuesection(fork, node)

            ET.SubElement(node, "section", className="ServiceTunnel")

            # generate fork section

            forkSection = ET.SubElement(node, "section", className="Fork")

            jobsParm = ET.SubElement(forkSection, "parameter", classPath="java.lang.Integer", name="jobsPerLink")
            ET.SubElement(jobsParm, "value").text = str(fork.num_tasks)

            blockParm = ET.SubElement(forkSection, "parameter", classPath="java.lang.Integer", name="block")
            ET.SubElement(blockParm, "value").text = "-1"

            simplifiedParm = ET.SubElement(forkSection, "parameter", classPath="java.lang.Boolean", name="isSimplifiedFork")
            ET.SubElement(simplifiedParm, "value").text = "true"

            forkstrategyParm = ET.SubElement(forkSection, "parameter", array="true", classPath="jmt.engine.NetStrategies.ForkStrategy", name="ForkStrategy")
            for jobclass in self.classes:
                ET.SubElement(forkstrategyParm, "refClass").text = jobclass.name
                branchsubParm = ET.SubElement(forkstrategyParm, "subParameter", classPath="jmt.engine.NetStrategies.ForkStrategies.ProbabilitiesFork", name="Branch Probabilities")
                empiricalentryarrayParm = ET.SubElement(branchsubParm, "subParameter", array="true", classPath="jmt.engine.NetStrategies.ForkStrategies.OutPath", name="EmpiricalEntryArray")
                for target in fork.links:
                    outpathentryParm = ET.SubElement(empiricalentryarrayParm, "subParameter", classPath="jmt.engine.NetStrategies.ForkStrategies.OutPath", name="OutPathEntry")

                    outunitprobabilityParm = ET.SubElement(outpathentryParm, "subParameter", classPath="jmt.engine.random.EmpiricalEntry", name="outUnitProbability")
                    staionnameParm = ET.SubElement(outunitprobabilityParm, "subParameter", classPath="java.lang.String", name="stationName")
                    ET.SubElement(staionnameParm, "value").text = target
                    probabilityParm = ET.SubElement(outunitprobabilityParm, "subParameter", classPath="java.lang.Double",
                                                   name="probability")
                    ET.SubElement(probabilityParm, "value").text = "1.0"


                    jobsperlinkParm = ET.SubElement(outpathentryParm, "subParameter", array="true", classPath="jmt.engine.random.EmpiricalEntry", name="JobsPerLinkDis")
                    empiricalEntryParm = ET.SubElement(jobsperlinkParm, "subParameter", classPath="jmt.engine.random.EmpiricalEntry", name="EmpiricalEntry")

                    numbersParm = ET.SubElement(empiricalEntryParm, "subParameter", classPath="java.lang.String",
                                                    name="numbers")
                    ET.SubElement(numbersParm, "value").text = "1"

                    probabilityParm = ET.SubElement(empiricalEntryParm, "subParameter", classPath="java.lang.Double",
                                                   name="probability")
                    ET.SubElement(probabilityParm, "value").text = "1.0"

        for join in self.nodes['joins']:
            node = ET.SubElement(sim, "node", name=join.name)

            ET.SubElement(node, "section", className="ServiceTunnel")

            # generate join section
            joinSection = ET.SubElement(node, "section", className="Join")
            parm = ET.SubElement(joinSection, "parameter", array="true", classPath="jmt.engine.NetStrategies.JoinStrategy", name="JoinStrategy")
            for jobclass in self.classes:
                ET.SubElement(parm, "refClass").text = jobclass.name
                outersubparm = ET.SubElement(parm, "subParameter", classPath="jmt.engine.NetStrategies.JoinStrategies.NormalJoin", name="Standard Join")
                innersubparm = ET.SubElement(outersubparm, "subParameter", classPath="java.lang.Integer", name="numRequired")
                ET.SubElement(innersubparm, "value").text = "-1"


            self.generate_router(join, node)



        for sink in self.nodes['sinks']:
            node = ET.SubElement(sim, "node", name=sink.name)
            ET.SubElement(node, "section", className="JobSink")

        measuresQueue = ["Number of Customers", "Utilization", "Response Time", "Throughput", "Arrival Rate"]
        for measure in measuresQueue:
            for queue in self.nodes['queues']:
                for oclass in queue.services.keys():
                    ET.SubElement(sim, "measure", alpha="0.01", name=f"{queue.name}_{oclass}_{measure}",
                                  nodeType="station",
                                  precision="0.03", referenceNode=queue.name, referenceUserClass=f"{oclass}",
                                  type=measure,
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
                    ET.SubElement(sim, "measure", alpha="0.01", name=f"{source.name}_{oclass}_{measure}",
                                  nodeType="station",
                                  precision="0.03", referenceNode=source.name, referenceUserClass=f"{oclass}",
                                  type=measure,
                                  verbose="false")

        for link in self.links:
            ET.SubElement(sim, "connection", source=link.source.name, target=link.target.name)

        openedPreloadTag = False
        for jobclass in self.classes:
            if isinstance(jobclass, ClosedClass):
                if not openedPreloadTag:
                    preload = ET.SubElement(sim, "preload")
                    openedPreloadTag = True
                stationPopulations = ET.SubElement(preload, "stationPopulations", stationName=jobclass.referenceSource)
                ET.SubElement(stationPopulations, "classPopulation", population=str(jobclass.population),
                                  refClass=jobclass.name)

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
            if routing is None:
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.RoutingStrategies.RandomStrategy",
                                             name="Random")
            elif routing["routing_strat"].value[0] == "Static":
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath=f"jmt.engine.NetStrategies.RoutingStrategies.{routing['routing_strat'].value[2]}",
                                             name=routing["routing_strat"].value[1])

            elif routing["routing_strat"].value[0] == "Variable":  # TODO IMPLEMENT THIS PROPERLY
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.RoutingStrategies.EmpiricalStrategy",
                                             name="Probabilities")
                empiricalEntryArray = ET.SubElement(subParameter, "subParameter", array="true",
                                                    classPath="jmt.engine.random.EmpiricalEntry",
                                                    name="EmpiricalEntryArray")

                for (target, val) in routing['probabilities']:
                    empiricalEntry = ET.SubElement(empiricalEntryArray, "subParameter",
                                                   classPath="jmt.engine.random.EmpiricalEntry", name="EmpiricalEntry")
                    stationName = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.String",
                                                name="stationName")
                    ET.SubElement(stationName, "value").text = target
                    probability = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.Double",
                                            name="probability")
                    ET.SubElement(probability, "value").text = str(float(val))

    def generate_classes(self, simTag):
        for jobclass in self.classes:
            if isinstance(jobclass, OpenClass):
                ET.SubElement(simTag, "userClass", name=jobclass.name, priority=str(jobclass.priority),
                              referenceSource=jobclass.referenceSource, type="open")

            elif isinstance(jobclass, ClosedClass):
                ET.SubElement(simTag, "userClass", customers=str(jobclass.population), name=jobclass.name,
                              priority=str(jobclass.priority),
                              referenceSource=jobclass.referenceSource, type="closed")

    def generate_servicestrategy(self, node, parentTag):
        parameter = ET.SubElement(parentTag, "parameter", array="true",
                                  classPath="jmt.engine.NetStrategies.ServiceStrategy", name="ServiceStrategy")
        for jobclass in self.classes:
            serviceDict = node.services.get(jobclass.name, {})
            service = serviceDict.get("service_strategy")

            ET.SubElement(parameter, "refClass").text = jobclass.name
            subParameter = ET.SubElement(parameter, "subParameter",
                                         classPath="jmt.engine.NetStrategies.ServiceStrategies.ServiceTimeStrategy",
                                         name="ServiceTimeStrategy")
            if isinstance(service, Cox):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.CoxianDistr",
                              name="Coxian")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.CoxianPar",
                                         name="distrPar")
                lambda0 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda0")
                ET.SubElement(lambda0, "value").text = str(float(service.lambda0))

                lambda1 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda1")
                ET.SubElement(lambda1, "value").text = str(float(service.lambda1))

                phi0 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="phi0")
                ET.SubElement(phi0, "value").text = str(float(service.p0))
            elif isinstance(service, Det):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.DeterministicDistr",
                              name="Deterministic")
                distrPar = ET.SubElement(subParameter, "subParameter",
                                         classPath="jmt.engine.random.DeterministicDistrPar",
                                         name="distrPar")
                t = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="t")
                ET.SubElement(t, "value").text = str(float(service.k))
            elif isinstance(service, Erlang):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Erlang",
                              name="Erlang")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ErlangPar",
                                         name="distrPar")
                alphaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                ET.SubElement(alphaPar, "value").text = str(float(service.lambda_value))
                rPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Long", name="r")
                ET.SubElement(rPar, "value").text = str(int(service.k))
            elif isinstance(service, Exp):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Exponential",
                              name="Exponential")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ExponentialPar",
                                         name="distrPar")
                lambdaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda")
                ET.SubElement(lambdaPar, "value").text = str(float(service.lambda_value))
            elif isinstance(service, Gamma):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.GammaDistr",
                              name="Gamma")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.GammaDistrPar",
                                         name="distrPar")
                alphaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                ET.SubElement(alphaPar, "value").text = str(float(service.alpha))
                beta = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="beta")
                ET.SubElement(beta, "value").text = str(float(service.theta))
            elif isinstance(service, HyperExp):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.HyperExp",
                              name="Hyperexponential")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.HyperExpPar",
                                         name="distrPar")
                p = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="p")
                ET.SubElement(p, "value").text = str(float(service.p))

                lambda1 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda1")
                ET.SubElement(lambda1, "value").text = str(float(service.lambda1))

                lambda2 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda2")
                ET.SubElement(lambda2, "value").text = str(float(service.lambda2))
            elif isinstance(service, Lognormal):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Lognormal",
                              name="Lognormal")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.LognormalPar",
                                         name="distrPar")
                alphaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="mu")
                ET.SubElement(alphaPar, "value").text = str(float(service.mu))
                beta = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="sigma")
                ET.SubElement(beta, "value").text = str(float(service.sigma))
            elif isinstance(service, Normal):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Normal",
                              name="Normal")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.NormalPar",
                                         name="distrPar")
                mean = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="mean")
                ET.SubElement(mean, "value").text = str(float(service.mean))
                standardDeviation = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double",
                                                  name="standardDeviation")
                ET.SubElement(standardDeviation, "value").text = str(float(service.standardDeviation))
            elif isinstance(service, Pareto):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Pareto",
                              name="Pareto")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ParetoPar",
                                         name="distrPar")
                alpha = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                ET.SubElement(alpha, "value").text = str(float(service.alpha))
                k = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="k")
                ET.SubElement(k, "value").text = str(float(service.k))
            elif isinstance(service, Replayer):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Replayer",
                              name="Replayer")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ReplayerPar",
                                         name="distrPar")
                lambdaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.String", name="fileName")
                ET.SubElement(lambdaPar, "value").text = service.fileName
            elif isinstance(service, Uniform):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Uniform",
                              name="Uniform")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.UniformPar",
                                         name="distrPar")
                min = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="min")
                ET.SubElement(min, "value").text = str(float(service.min))
                max = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="max")
                ET.SubElement(max, "value").text = str(float(service.max))
            elif isinstance(service, Weibull):
                ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Weibull",
                              name="Weibull")
                distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.WeibullPar",
                                         name="distrPar")
                alpha = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                ET.SubElement(alpha, "value").text = str(float(service.lambda_value))
                r = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="r")
                ET.SubElement(r, "value").text = str(float(service.k))
            else:
                ET.SubElement(subParameter, "value").text = "null"

    def generate_queuesection(self, node, parentTag):

        section = ET.SubElement(parentTag, "section", className="Queue")
        # TODO ADD DIFFERENT CAPACITIES BASED ON QUEUE
        sizepar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="size")
        if hasattr(node, 'capacity'):
            ET.SubElement(sizepar, "value").text = str(node.capacity)
        else:
            ET.SubElement(sizepar, "value").text = "-1"

        dropStrategies = ET.SubElement(section, "parameter", array="true", classPath="java.lang.String",
                                       name="dropStrategies")

        # TODO FIGURE OUT WHAT CAUSES DROP TYPE TO CHANGE
        # TODO UPDATE SEEMS LIKE IT DOESNT MATTER WHEN CAPACITY IS INFINITE
        drop = "drop"
        if isinstance(node, Queue):
            # TODO DO THIS PROPERLY
            drop = "drop"

        for jobclass in self.classes:
            ET.SubElement(dropStrategies, "refClass").text = jobclass.name
            dropStrategy = ET.SubElement(dropStrategies, "subParameter", classPath="java.lang.String",
                                         name="dropStrategy")
            ET.SubElement(dropStrategy, "value").text = drop

        # TODO CLARIFY IF QUEUEGETSTRATEGIES IS ALWAYS FCFS
        ET.SubElement(section, "parameter",
                      classPath="jmt.engine.NetStrategies.QueueGetStrategies.FCFSstrategy", name="FCFSstrategy")
        parameter = ET.SubElement(section, "parameter", array="true",
                                  classPath="jmt.engine.NetStrategies.QueuePutStrategy",
                                  name="QueuePutStrategy")

        for jobclass in self.classes:
            if isinstance(node, Queue):
                ET.SubElement(parameter, "refClass").text = jobclass.name
                ET.SubElement(parameter, "subParameter",
                              classPath=f"jmt.engine.NetStrategies.QueuePutStrategies.{node.strategy.value[1]}",
                              name=node.strategy.value[1])
            else:
                ET.SubElement(parameter, "refClass").text = jobclass.name
                ET.SubElement(parameter, "subParameter",
                              classPath="jmt.engine.NetStrategies.QueuePutStrategies.TailStrategy", name="TailStrategy")

    def generate_serversection(self, node: Queue, parentTag):
        serverclassname = ""
        if node.strategy.value[0] == "NP":
            serverclassname = "Server"
        elif node.strategy.value[0] == "PS":
            serverclassname = "PSServer"
        elif node.strategy.value[0] == "P":
            serverclassname = "PreemptiveServer"
        section = ET.SubElement(parentTag, "section", className=serverclassname)
        maxJobsPar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="maxJobs")
        ET.SubElement(maxJobsPar, "value").text = str(node.numberOfServers)

        if serverclassname == "PSServer":
            maxRunningPar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="maxRunning")
            ET.SubElement(maxRunningPar, "value").text = "-1"

        parameter = ET.SubElement(section, "parameter", array="true", classPath="java.lang.Integer",
                                  name="numberOfVisits")

        # TODO SEE IF THIS IS CONSTANT
        for jobclass in self.classes:
            ET.SubElement(parameter, "refClass").text = jobclass.name
            numberOfVisits = ET.SubElement(parameter, "subParameter", classPath="java.lang.Integer",
                                           name="numberOfVisits")
            ET.SubElement(numberOfVisits, "value").text = "1"

        self.generate_servicestrategy(node, section)

        if serverclassname == "PreemptiveServer":
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.QueuePutStrategy", name="PreemptiveStrategy")
            for jobclass in self.classes:
                ET.SubElement(parameter, "refClass").text = jobclass.name
                ET.SubElement(parameter, "subParameter",
                              classPath=f"jmt.engine.NetStrategies.QueuePutStrategies.{node.strategy.value[1]}",
                              name=node.strategy.value[1])

        if serverclassname == "PSServer":
            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="jmt.engine.NetStrategies.PSStrategy", name="PSStrategy")
            for jobclass in self.classes:
                ET.SubElement(parameter, "refClass").text = jobclass.name
                ET.SubElement(parameter, "subParameter",
                              classPath=f"jmt.engine.NetStrategies.PSStrategies.{node.strategy.value[2]}",
                              name=f"{node.strategy.value[2]}")

            parameter = ET.SubElement(section, "parameter", array="true",
                                      classPath="java.lang.Double", name="serviceWeights")
            for jobclass in self.classes:
                ET.SubElement(parameter, "refClass").text = jobclass.name
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="java.lang.Double",
                                             name="serviceWeight")
                ET.SubElement(subParameter, "value").text = str(node.services[jobclass.name]["weight"])

    def generate_classswitchsection(self, node, parentTag):
        section = ET.SubElement(parentTag, "section", className="ClassSwitch")
        parameter = ET.SubElement(section, "parameter", classPath="java.lang.Object", array="true", name="matrix")
        for class1 in node.p.keys():
            ET.SubElement(parameter, "refClass").text = str(class1)
            subParameter = ET.SubElement(parameter, "subParameter", classPath="java.lang.Float", array="true", name="row")
            for class2 in node.p[class1]:
                ET.SubElement(subParameter, "refClass").text = str(class2)
                subParameter2 = ET.SubElement(subParameter, "subParameter", classPath="java.lang.Float", name="cell")
                ET.SubElement(subParameter2, "value").text = str(float(node.p[class1][class2]))
