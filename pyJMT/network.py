import xml.etree.ElementTree as ET
from .nodes import Source, Sink, Queue, Delay, Router, Fork, Join, RoutingSection
from .classes import OpenClass, ClosedClass
from .service_distributions import Cox, Det, Disabled, Exp, Erlang, Gamma, HyperExp, Lognormal, Normal, Pareto, \
    Replayer, Uniform, Weibull, ZeroServiceTime
from .link import Link
import os
import subprocess
from itertools import product
import tempfile
import requests
from datetime import datetime

JMTPath = None
def installJMT():
    global JMTPath
    if JMTPath is None:
        if not os.path.isfile("JMT.jar"):
            # If not, download it
            print(f"JMT.jar does not exist. Downloading from http://jmt.sourceforge.net/latest/JMT.jar")
            response = requests.get("http://jmt.sourceforge.net/latest/JMT.jar")
            with open("JMT.jar", 'wb') as f:
                f.write(response.content)
        JMTPath = os.path.join(os.getcwd(), "JMT.jar")

def add_extension_if_none(filename, extension):
    base_name, ext = os.path.splitext(filename)
    if not ext:
        return f"{filename}.{extension}"
    else:
        return filename

def saveResultsFromJsimgFile(fileName, seed=None, maxTime=600):
    """
    Runs a simulation and generates a JMT results file with the given fileName

    :param fileName: The file name for the results file to be given.
    :type fileName: str
    :param seed: The seed for the simulation. Leave blank or as None for a random seed
    :type seed: int, optional
    :param maxTime: The maximum time for the simulation to run. Default is 600 seconds
    :type maxTime: int, optional
    """
    global JMTPath
    dir_path = os.path.join(os.getcwd(), "output_files")
    os.makedirs(dir_path, exist_ok=True)
    adds = " "
    if not seed is None:
        adds += f"-seed {seed} "
    if not maxTime is None:
        adds += f"-maxtime {maxTime} "

    cmd = f'java -cp "{JMTPath}" jmt.commandline.Jmt sim "{os.path.join(dir_path, add_extension_if_none(fileName, "jsimg"))}" {adds}'
    print(cmd)
    subprocess.run(cmd, shell=True)

def printResultsFromResultsFile(fileName):
    """
    Prints results to console from a JMT results file

    :param fileName: The file name for the results file to print from.
    :type fileName: str
    """
    dir_path = os.path.join(os.getcwd(), "output_files")
    filewithext = add_extension_if_none(fileName, 'jsimg')
    tree = ET.parse(f'{os.path.join(dir_path, f"{filewithext}-result.jsim")}')
    root = tree.getroot()

    # Extract the model name from the root element
    model_name = root.attrib.get('modelName', 'Unknown Model')

    # Get all measures from the XML
    measures = [measure.attrib for measure in root.findall('measure')]

    # Sort the measures by station and then by class
    measures_sorted = sorted(measures, key=lambda x: (x['station'], x['class']))

    # Get unique attribute names from all measures
    unique_attributes = set()
    for measure in measures_sorted:
        unique_attributes.update(measure.keys())

    # Create a dictionary to store the column widths and initialize with the lengths of column headers
    col_widths = {attr: len(attr) for attr in unique_attributes}

    # Update column widths based on the length of attribute values in the measures
    for measure in measures_sorted:
        for attr in unique_attributes:
            col_widths[attr] = max(col_widths[attr], len(measure.get(attr, 'N/A')))

    # Print the column headers with Station and JobClass as the first two columns
    print(f"{'Station':<{col_widths['station']}} {'JobClass':<{col_widths['class']}}", end=" ")
    for attr in unique_attributes:
        if attr not in ['station', 'class']:
            print(f"{attr:<{col_widths[attr]}}", end=" ")
    print()

    # Print the table rows
    for measure in measures_sorted:
        station = measure['station']
        job_class = measure['class']
        print(f"{station:<{col_widths['station']}} {job_class:<{col_widths['class']}}", end=" ")
        for attr in unique_attributes:
            if attr not in ['station', 'class']:
                print(f"{measure.get(attr, 'N/A'):<{col_widths[attr]}}", end=" ")
        print()

def getResultsFromResultsFile(fileName):
    """
    Returns a dictionary of the results from a results file

    :param fileName: The file name for the results file to print from.
    :type fileName: str
    """
    dir_path = os.path.join(os.getcwd(), "output_files")
    filewithext = add_extension_if_none(fileName, 'jsimg')
    tree = ET.parse(f'{os.path.join(dir_path, f"{filewithext}-result.jsim")}')
    root = tree.getroot()

    # Extract the model name from the root element
    model_name = root.attrib.get('modelName', 'Unknown Model')

    # Get all measures from the XML
    measures = [measure.attrib for measure in root.findall('measure')]

    # Sort the measures by station and then by class
    measures_sorted = sorted(measures, key=lambda x: (x['station'], x['class']))

    # Get unique attribute names from all measures
    unique_attributes = set()
    for measure in measures_sorted:
        unique_attributes.update(measure.keys())

    # Prepare the final dictionary
    results = {}

    # Populate the dictionary
    for measure in measures_sorted:
        station = measure['station']
        job_class = measure['class']

        # Initialize dictionaries if they don't exist yet
        if station not in results:
            results[station] = {}
        if job_class not in results[station]:
            results[station][job_class] = {}

        # Populate the job class dictionary
        for attr in unique_attributes:
            if attr not in ['station', 'class']:
                results[station][job_class][attr] = measure.get(attr, 'N/A')

    return results


class Network:
    """
    A class to represent a network.
    """

    def __init__(self, name, maxTime=600, maxSamples=1000000):
        """
             Constructs all the necessary attributes for the network object.

             :param name: Name of the network.
             :type name: str
             :param maxTime: Maximum simulation time of the network in seconds. Default is 600 seconds.
             :type maxTime: int, optional
             :param maxSamples: Maximum number of samples in the simulation of the network. Default is 1000000.
             :type maxSamples: int, optional
             """
        self.name = name
        self.nodes = {'sources': [], 'sinks': [], 'queues': [], 'delays': [],
                      'routers': [], 'classswitches': [], 'forks': [], 'joins': [],
                      'loggers': [], 'fcrs': []}
        self.links: [Link] = []
        self.classes = []
        self.defaultMetrics = True
        self.additionalMetrics = []
        self.maxSamples = maxSamples
        self.maxTime = maxTime
        self.logDelimiter = ";"
        # Check if file exists
        installJMT()


    def removeNode(self, node):
        """
           Removes a node from the network

           :param node: The node to remove from this Network.
           :type node: Node
        """
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[i])):
                if self.nodes[i][j] == node:
                    self.nodes[i].remove(node)

    def useDefaultMetrics(self, trueorfalse):
        """
           Set whether to use the default metrics. True by default.

           :param trueorfalse: The bool to set this parameter to
           :type trueorfalse: bool
        """
        self.defaultMetrics = trueorfalse

    def get_number_of_nodes(self):
        total_length = sum(len(v) for v in self.nodes.values())
        return total_length

    def get_number_of_classes(self):
        return len(self.classes)

    def get_nodes(self):
        return [value for sublist in self.nodes.values() for value in sublist]

    def get_classes(self):
        return self.classes

    def addMetric(self, jobclass, node, metric):
        """
             Adds a metric to a node and jobclass combination

             :param jobclass: The jobclass to add this parameter to
             :type jobclass: JobClass
             :param node: The node to add this metric to
             :type node: Node
             :param metric: The metric to add
             :type metric: Metrics
        """
        self.additionalMetrics.append((jobclass, node, metric))

    def addLink(self, source, target):
        """
            Adds a link between two nodes

            :param source: The start node of the link
            :type source: Node
            :param target: The end node of the link
            :type target: Node
        """
        # Adds links onto fork object to avoid having to search through
        # the links later, this problem only occurs when generating xml
        # for forks
        if isinstance(source, Fork):
            source.links.append(target.name)
        link = Link(source, target)
        self.links.append(link)

    def addLinks(self, linkList):
        """
            Adds many links between nodes, takes in a list of pairs of nodes.

            :param linkList: The list of pairs of nodes to add links for.
            :type linkList: [(Node, Node)]
        """
        for source, target in linkList:
            self.addLink(source, target)

    def link(self, p):
        """
            Adds many between links nodes, takes in a routing matrix.

            :param p: The routing matrix.
            :type p: Routing Matrix
        """
        for linkClass, classDict in p.items():
            if len(classDict) == 0:
                continue
            else:
                if isinstance(linkClass, tuple):
                    # generate classswitch
                    c1, c2 = linkClass
                    for source, target in classDict:
                        source.setClassSwitchRouting(c1, c2, target, p[c1].get((source, target), 1.0),
                                                     p[(c1, c2)][(source, target)])

                for (n1, n2) in classDict:
                    containsAlready = False
                    for link in self.links:
                        if link.source == n1 and link.target == n2:
                            containsAlready = True
                            break
                    if containsAlready:
                        break
                    else:
                        self.addLink(n1, n2)

    def removeLink(self, source, target):
        """
           Removes a link between two nodes.

           :param source: The start node of the link.
           :type source: Node
           :param target: The end node of the link.
           :type target: Node
        """
        # Adds links onto fork object to avoid having to search through
        # the links later, this problem only occurs when generating xml
        # for forks
        if isinstance(source, Fork):
            source.links.remove(target.name)
        link = [x for x in self.links if x.source == source and x.target == target]
        self.links.remove(link[0])

    def removeLinks(self, linkList):
        """
        Removes many links between nodes, takes in a list of pairs of nodes.

        :param linkList: The list of pairs of nodes to remove links for.
        :type linkList: [(Node, Node)]
        """
        for source, target in linkList:
            self.removeLink(source, target)

    def jsimgOpen(self):
        """
            Opens the Network in JMT, very useful for debugging
        """
        global JMTPath
        dir_path = os.path.join(os.getcwd(), "output_files")
        os.makedirs(dir_path, exist_ok=True)

        # Create a temporary file in the specific directory
        with tempfile.NamedTemporaryFile(dir=dir_path, delete=False) as temp:
            self.generate_xml(os.path.join(dir_path, f"{temp.name}"))
            cmd = f'java -cp "{JMTPath}" jmt.commandline.Jmt jsimg "{os.path.join(dir_path, f"{temp.name}")}"'
            subprocess.run(cmd, shell=True)

        os.unlink(os.path.join(dir_path, f"{temp.name}"))

    def saveNamedJsimg(self, fileName):
        """
        Saves the current network to a file in output_files with a given name.

        :param fileName: The name of the file.
        :type fileName: str
         """
        dir_path = os.path.join(os.getcwd(), "output_files")
        os.makedirs(dir_path, exist_ok=True)
        self.generate_xml(os.path.join(dir_path, add_extension_if_none(fileName, "jsimg")))

    def saveTempJsimg(self):
        """
           Saves the current network to a file in output_files with a temporary name and returns the name.

           :return: temporary file name
           :rtype: str
        """
        dir_path = os.path.join(os.getcwd(), "output_files")
        os.makedirs(dir_path, exist_ok=True)

        # Create a temporary file in the specific directory
        with tempfile.NamedTemporaryFile(dir=dir_path, suffix=".jsimg", delete=False) as temp:
            self.generate_xml(os.path.join(dir_path, add_extension_if_none(temp.name, "jsimg")))

        return add_extension_if_none(temp.name, "jsimg")

    def saveResultsFileNamed(self, fileName, seed=None):
        """
        Runs a simulation and generates a JMT results file with the given fileName from this Network as well as a Jsimg file

        :param fileName: The file name for the results file to be given.
        :type fileName: str
        :param seed: The seed for the simulation.
        :type seed: int, optional
        """
        self.saveNamedJsimg(fileName)
        saveResultsFromJsimgFile(fileName, seed)

    def printResults(self, seed=None):
        """
               Prints results to console without saving anything

                :param seed: The seed for the simulation.
                :type seed: int, optional
           """
        tempfileName = self.saveTempJsimg()
        self.saveResultsFileNamed(tempfileName, seed)
        printResultsFromResultsFile(tempfileName)
        dir = os.path.join(os.getcwd(), "output_files")
        os.unlink(os.path.join(dir, add_extension_if_none(tempfileName, "jsimg")))
        os.unlink(os.path.join(dir, f'{add_extension_if_none(tempfileName, "jsimg")}-result.jsim'))

    def getResults(self, seed=None):
        """
        Returns a dictionary of the results from the current network's simulation without saving anything.

        :param seed: The seed for the simulation.
        :type seed: int, optional
        """
        tempfileName = self.saveTempJsimg()
        self.saveResultsFileNamed(tempfileName, seed)
        dict = getResultsFromResultsFile(tempfileName)
        dir = os.path.join(os.getcwd(), "output_files")
        os.unlink(os.path.join(dir, add_extension_if_none(tempfileName, "jsimg")))
        os.unlink(os.path.join(dir, f'{add_extension_if_none(tempfileName, "jsimg")}-result.jsim'))
        return dict

    def init_routing_matrix(self):
        """
               Creates and returns a routing matrix for use with Network.link

                :return: Routing Matrix p
           """
        # TODO see if this is ok
        classes = self.get_classes()

        P = {}
        # For P[class_name][node_name][node_name]
        for c in classes:
            P[c] = {}

        # For P[class_name][class_name][node_name][node_name]
        for c1, c2 in product(classes, repeat=2):
            P[(c1, c2)] = {}

        return P

    def generate_xml(self, fileName, seed=1234, maxTime=None):
        ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

        root = ET.Element("archive",
                          attrib={"name": os.path.basename(fileName),
                                  "timestamp": datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y"),
                                  "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation": "Archive.xsd"})

        disableStatisticsStop = "false"
        if not maxTime is None:
            disableStatisticsStop = "true"

        sim = ET.SubElement(root, "sim",
                            attrib={"disableStatisticStop": f"{disableStatisticsStop}",
                                    "logDecimalSeparator": ".",
                                    "logDelimiter": f"{self.logDelimiter}",
                                    "logPath": "/global/",
                                    "logReplaceMode": "0",
                                    "maxEvents": "-1",
                                    "maxSamples": str(self.maxSamples),
                                    "name": os.path.basename(fileName),
                                    "seed": str(seed),
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

            simplifiedParm = ET.SubElement(forkSection, "parameter", classPath="java.lang.Boolean",
                                           name="isSimplifiedFork")
            ET.SubElement(simplifiedParm, "value").text = "true"

            forkstrategyParm = ET.SubElement(forkSection, "parameter", array="true",
                                             classPath="jmt.engine.NetStrategies.ForkStrategy", name="ForkStrategy")
            for jobclass in self.classes:
                ET.SubElement(forkstrategyParm, "refClass").text = jobclass.name
                branchsubParm = ET.SubElement(forkstrategyParm, "subParameter",
                                              classPath="jmt.engine.NetStrategies.ForkStrategies.ProbabilitiesFork",
                                              name="Branch Probabilities")
                empiricalentryarrayParm = ET.SubElement(branchsubParm, "subParameter", array="true",
                                                        classPath="jmt.engine.NetStrategies.ForkStrategies.OutPath",
                                                        name="EmpiricalEntryArray")
                for target in fork.links:
                    outpathentryParm = ET.SubElement(empiricalentryarrayParm, "subParameter",
                                                     classPath="jmt.engine.NetStrategies.ForkStrategies.OutPath",
                                                     name="OutPathEntry")

                    outunitprobabilityParm = ET.SubElement(outpathentryParm, "subParameter",
                                                           classPath="jmt.engine.random.EmpiricalEntry",
                                                           name="outUnitProbability")
                    staionnameParm = ET.SubElement(outunitprobabilityParm, "subParameter", classPath="java.lang.String",
                                                   name="stationName")
                    ET.SubElement(staionnameParm, "value").text = target
                    probabilityParm = ET.SubElement(outunitprobabilityParm, "subParameter",
                                                    classPath="java.lang.Double",
                                                    name="probability")
                    ET.SubElement(probabilityParm, "value").text = "1.0"

                    jobsperlinkParm = ET.SubElement(outpathentryParm, "subParameter", array="true",
                                                    classPath="jmt.engine.random.EmpiricalEntry", name="JobsPerLinkDis")
                    empiricalEntryParm = ET.SubElement(jobsperlinkParm, "subParameter",
                                                       classPath="jmt.engine.random.EmpiricalEntry",
                                                       name="EmpiricalEntry")

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
            parm = ET.SubElement(joinSection, "parameter", array="true",
                                 classPath="jmt.engine.NetStrategies.JoinStrategy", name="JoinStrategy")
            for jobclass in self.classes:
                ET.SubElement(parm, "refClass").text = jobclass.name
                outersubparm = ET.SubElement(parm, "subParameter",
                                             classPath="jmt.engine.NetStrategies.JoinStrategies.NormalJoin",
                                             name="Standard Join")
                innersubparm = ET.SubElement(outersubparm, "subParameter", classPath="java.lang.Integer",
                                             name="numRequired")
                ET.SubElement(innersubparm, "value").text = "-1"

            self.generate_router(join, node)

        for logger in self.nodes['loggers']:
            node = ET.SubElement(sim, "node", name=logger.name)

            self.generate_queuesection(logger, node)

            section = ET.SubElement(node, "section", className="LogTunnel")

            parm = ET.SubElement(section, "parameter", classPath="java.lang.String", name="logfileName")
            ET.SubElement(parm, "value").text = logger.logfileName
            parm = ET.SubElement(section, "parameter", classPath="java.lang.String", name="logfilePath")
            ET.SubElement(parm, "value").text = logger.logfilePath

            parm = ET.SubElement(section, "parameter", classPath="java.lang.Boolean", name="logExecTimestamp")
            ET.SubElement(parm, "value").text = str(logger.startTime).lower()

            parm = ET.SubElement(section, "parameter", classPath="java.lang.Boolean", name="logLoggerName")
            ET.SubElement(parm, "value").text = str(logger.logLoggerName).lower()

            parm = ET.SubElement(section, "parameter", classPath="java.lang.Boolean", name="logTimeStamp")
            ET.SubElement(parm, "value").text = str(logger.timestamp).lower()

            parm = ET.SubElement(section, "parameter", classPath="java.lang.Boolean", name="logJobID")
            ET.SubElement(parm, "value").text = str(logger.jobID).lower()

            parm = ET.SubElement(section, "parameter", classPath="java.lang.Boolean", name="logJobClass")
            ET.SubElement(parm, "value").text = str(logger.jobclass).lower()

            parm = ET.SubElement(section, "parameter", classPath="java.lang.Boolean", name="logTimeSameClass")
            ET.SubElement(parm, "value").text = str(logger.timeSameClass).lower()

            parm = ET.SubElement(section, "parameter", classPath="java.lang.Boolean", name="logTimeAnyClass")
            ET.SubElement(parm, "value").text = str(logger.timeAnyClass).lower()

            parm = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="numClasses")
            ET.SubElement(parm, "value").text = str(len(self.classes))

            self.generate_router(logger, node)

        for sink in self.nodes['sinks']:
            node = ET.SubElement(sim, "node", name=sink.name)
            ET.SubElement(node, "section", className="JobSink")

        for fcr in self.nodes['fcrs']:
            blockingRegion = ET.SubElement(sim, "blockingRegion", name=fcr.name, type="default")
            ET.SubElement(blockingRegion, "regionNode", nodeName=fcr.nodeName)
            ET.SubElement(blockingRegion, "globalConstraint", maxJobs=str(fcr.maxCapacity))
            ET.SubElement(blockingRegion, "globalMemoryConstraint", maxMemory=str(fcr.maxMemory))

            for jobclass in self.classes:
                ET.SubElement(blockingRegion, "classConstraint", jobClass=jobclass.name,
                              maxJobsPerClass=str(fcr.classMaxCapacities.get(jobclass.name, -1)))
            for jobclass in self.classes:
                ET.SubElement(blockingRegion, "classMemoryConstraint", jobClass=jobclass.name,
                              maxMemoryPerClass=str(fcr.classMaxMemories.get(jobclass.name, -1)))
            for jobclass in self.classes:
                ET.SubElement(blockingRegion, "dropRules",
                              dropThisClass=str(fcr.dropRules.get(jobclass.name, False)).lower(),
                              jobClass=jobclass.name)
            for jobclass in self.classes:
                ET.SubElement(blockingRegion, "classWeight", jobClass=jobclass.name,
                              weight=str(fcr.classWeights.get(jobclass.name, 1)))
            for jobclass in self.classes:
                ET.SubElement(blockingRegion, "classSize", jobClass=jobclass.name,
                              size=str(fcr.classSizes.get(jobclass.name, 1)))

        self.generate_metrics(sim)

        for link in self.links:
            ET.SubElement(sim, "connection", source=link.source.name, target=link.target.name)

        openedPreloadTag = False
        for jobclass in self.classes:
            if isinstance(jobclass, ClosedClass) and jobclass.population != 0:
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

    def generate_metrics(self, sim):
        if self.defaultMetrics:
            # TODO CHECK WHAT DEFAULTS SHOULD BE EXACTLY
            measuresQueue = ["Number of Customers", "Utilization", "Response Time", "Throughput", "Arrival Rate"] #TODO RESIDENCE TIME
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

        for (jobclass, node, metric) in self.additionalMetrics:
            if isinstance(node, Network):
                ET.SubElement(sim, "measure", alpha="0.01", name=f"{jobclass.name}_System {metric.value}",
                              nodeType="",
                              precision="0.03", referenceNode="", referenceUserClass=jobclass.name,
                              type=f"System {metric.value}",
                              verbose="false")
            else:
                ET.SubElement(sim, "measure", alpha="0.01", name=f"{node.name}_{jobclass.name}_{metric.value}",
                              nodeType="station",
                              precision="0.03", referenceNode=node.name, referenceUserClass=jobclass.name,
                              type=metric.value,
                              verbose="false")

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

            elif routing["routing_strat"].value[0] == "Prob":
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.RoutingStrategies.EmpiricalStrategy",
                                             name=routing["routing_strat"].value[1])
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

            elif routing["routing_strat"].value[0] == "ClassSwitch":
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath=f"jmt.engine.NetStrategies.RoutingStrategies.{routing['routing_strat'].value[2]}",
                                             name=routing["routing_strat"].value[1])
                routingParameterArray = ET.SubElement(subParameter, "subParameter", array="true",
                                                      classPath="jmt.engine.NetStrategies.RoutingStrategies.ClassSwitchRoutingParameter",
                                                      name="ClassSwitchRoutingParameterArray")

                for (target, routeprob) in routing['classswitchprobs'].keys():
                    routingParameter = ET.SubElement(routingParameterArray, "subParameter",
                                                     classPath="jmt.engine.NetStrategies.RoutingStrategies.ClassSwitchRoutingParameter",
                                                     name="ClassSwitchRoutingParameter")

                    stationNameParameter = ET.SubElement(routingParameter, "subParameter", classPath="java.lang.String",
                                                         name="stationName")
                    ET.SubElement(stationNameParameter, "value").text = target

                    probParameter = ET.SubElement(routingParameter, "subParameter", classPath="java.lang.Double",
                                                  name="probability")
                    ET.SubElement(probParameter, "value").text = str(self.roundedFraction(routeprob))

                    empiricalEntryArray = ET.SubElement(routingParameter, "subParameter", array="true",
                                                        classPath="jmt.engine.random.EmpiricalEntry",
                                                        name="EmpiricalEntryArray")
                    for targetjobclass in self.classes:
                        classchangeprob = routing['classswitchprobs'][(target, routeprob)].get(targetjobclass, 0.0)
                        empiricalEntry = ET.SubElement(empiricalEntryArray, "subParameter",
                                                       classPath="jmt.engine.random.EmpiricalEntry",
                                                       name="EmpiricalEntry")
                        className = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.String",
                                                  name="className")
                        ET.SubElement(className, "value").text = targetjobclass.name
                        probability = ET.SubElement(empiricalEntry, "subParameter", classPath="java.lang.Double",
                                                    name="probability")
                        ET.SubElement(probability, "value").text = str(self.roundedFraction(classchangeprob))

    def generate_classes(self, simTag):
        for jobclass in self.classes:
            if isinstance(jobclass, OpenClass):
                ET.SubElement(simTag, "userClass", name=jobclass.name, priority=str(jobclass.priority),
                              referenceSource=jobclass.referenceSource, type="open")

            elif isinstance(jobclass, ClosedClass):
                ET.SubElement(simTag, "userClass", customers=str(jobclass.population), name=jobclass.name,
                              priority=str(jobclass.priority),
                              referenceSource=jobclass.referenceSource, type="closed")

    def roundedFraction(self, num):
        rounded_num = round(num, 12) if num != int(num) else float(int(num))
        return rounded_num

    def generate_servicestrategy(self, node, parentTag):
        parameter = ET.SubElement(parentTag, "parameter", array="true",
                                  classPath="jmt.engine.NetStrategies.ServiceStrategy", name="ServiceStrategy")
        for jobclass in self.classes:
            serviceDict = node.services.get(jobclass.name, {})
            service = serviceDict.get("service_strategy")

            ET.SubElement(parameter, "refClass").text = jobclass.name
            if isinstance(service, Disabled):
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.ServiceStrategies.DisabledServiceTimeStrategy",
                                             name="DisabledServiceTimeStrategy")
            elif isinstance(service, ZeroServiceTime):
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.ServiceStrategies.ZeroServiceTimeStrategy",
                                             name="ZeroServiceTimeStrategy")
            else:
                subParameter = ET.SubElement(parameter, "subParameter",
                                             classPath="jmt.engine.NetStrategies.ServiceStrategies.ServiceTimeStrategy",
                                             name="ServiceTimeStrategy")
                if isinstance(service, Cox):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.CoxianDistr",
                                  name="Coxian")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.CoxianPar",
                                             name="distrPar")
                    lambda0 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda0")
                    ET.SubElement(lambda0, "value").text = str(self.roundedFraction(service.lambda0))

                    lambda1 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda1")
                    ET.SubElement(lambda1, "value").text = str(self.roundedFraction(service.lambda1))

                    phi0 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="phi0")
                    ET.SubElement(phi0, "value").text = str(self.roundedFraction(service.p0))
                elif isinstance(service, Det):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.DeterministicDistr",
                                  name="Deterministic")
                    distrPar = ET.SubElement(subParameter, "subParameter",
                                             classPath="jmt.engine.random.DeterministicDistrPar",
                                             name="distrPar")
                    t = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="t")
                    ET.SubElement(t, "value").text = str(self.roundedFraction(service.k))
                elif isinstance(service, Erlang):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Erlang",
                                  name="Erlang")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ErlangPar",
                                             name="distrPar")
                    alphaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                    ET.SubElement(alphaPar, "value").text = str(self.roundedFraction(service.lambda_value))
                    rPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Long", name="r")
                    ET.SubElement(rPar, "value").text = str(service.k)
                elif isinstance(service, Exp):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Exponential",
                                  name="Exponential")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ExponentialPar",
                                             name="distrPar")
                    lambdaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda")
                    ET.SubElement(lambdaPar, "value").text = str(self.roundedFraction(service.lambda_value))
                elif isinstance(service, Gamma):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.GammaDistr",
                                  name="Gamma")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.GammaDistrPar",
                                             name="distrPar")
                    alphaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                    ET.SubElement(alphaPar, "value").text = str(self.roundedFraction(service.alpha))
                    beta = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="beta")
                    ET.SubElement(beta, "value").text = str(self.roundedFraction(service.theta))
                elif isinstance(service, HyperExp):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.HyperExp",
                                  name="Hyperexponential")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.HyperExpPar",
                                             name="distrPar")
                    p = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="p")
                    ET.SubElement(p, "value").text = str(self.roundedFraction(service.p))

                    lambda1 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda1")
                    ET.SubElement(lambda1, "value").text = str(self.roundedFraction(service.lambda1))

                    lambda2 = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="lambda2")
                    ET.SubElement(lambda2, "value").text = str(self.roundedFraction(service.lambda2))
                elif isinstance(service, Lognormal):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Lognormal",
                                  name="Lognormal")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.LognormalPar",
                                             name="distrPar")
                    alphaPar = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="mu")
                    ET.SubElement(alphaPar, "value").text = str(self.roundedFraction(service.mu))
                    beta = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="sigma")
                    ET.SubElement(beta, "value").text = str(self.roundedFraction(service.sigma))
                elif isinstance(service, Normal):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Normal",
                                  name="Normal")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.NormalPar",
                                             name="distrPar")
                    mean = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="mean")
                    ET.SubElement(mean, "value").text = str(self.roundedFraction(service.mean))
                    standardDeviation = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double",
                                                      name="standardDeviation")
                    ET.SubElement(standardDeviation, "value").text = str(self.roundedFraction(service.standardDeviation))
                elif isinstance(service, Pareto):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Pareto",
                                  name="Pareto")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.ParetoPar",
                                             name="distrPar")
                    alpha = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                    ET.SubElement(alpha, "value").text = str(self.roundedFraction(service.alpha))
                    k = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="k")
                    ET.SubElement(k, "value").text = str(self.roundedFraction(service.k))
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
                    ET.SubElement(min, "value").text = str(self.roundedFraction(service.min))
                    max = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="max")
                    ET.SubElement(max, "value").text = str(self.roundedFraction(service.max))
                elif isinstance(service, Weibull):
                    ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.Weibull",
                                  name="Weibull")
                    distrPar = ET.SubElement(subParameter, "subParameter", classPath="jmt.engine.random.WeibullPar",
                                             name="distrPar")
                    alpha = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="alpha")
                    ET.SubElement(alpha, "value").text = str(self.roundedFraction(service.lambda_value))
                    r = ET.SubElement(distrPar, "subParameter", classPath="java.lang.Double", name="r")
                    ET.SubElement(r, "value").text = str(self.roundedFraction(service.k))
                else:
                    ET.SubElement(subParameter, "value").text = "null"

    def generate_queuesection(self, node, parentTag):

        section = ET.SubElement(parentTag, "section", className="Queue")
        sizepar = ET.SubElement(section, "parameter", classPath="java.lang.Integer", name="size")
        if hasattr(node, 'capacity'):
            ET.SubElement(sizepar, "value").text = str(node.capacity)
        else:
            ET.SubElement(sizepar, "value").text = "-1"

        dropStrategies = ET.SubElement(section, "parameter", array="true", classPath="java.lang.String",
                                       name="dropStrategies")

        drop = "drop"
        if isinstance(node, Queue):
            drop = node.dropRule.value

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
            subParameter = ET.SubElement(parameter, "subParameter", classPath="java.lang.Float", array="true",
                                         name="row")
            for class2 in node.p[class1]:
                ET.SubElement(subParameter, "refClass").text = str(class2)
                subParameter2 = ET.SubElement(subParameter, "subParameter", classPath="java.lang.Float", name="cell")
                ET.SubElement(subParameter2, "value").text = str(float(node.p[class1][class2]))
