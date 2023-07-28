import os
import unittest
import pyJMT as pj
import xml.etree.ElementTree as ET


def elements_equal(e1, e2, path=''):
    if e1.tag != e2.tag:
        print(f"Different tag at {path}: {e1.tag} != {e2.tag}")
        return False
    if (e1.text or '').strip() != (e2.text or '').strip():
        # Check if the text is a filename
        def get_filename_from_path(path):
            # Replace backslashes with forward slashes for Windows paths
            normalized_path = path.replace("\\", "/")
            # Return the last component of the path
            return normalized_path.split("/")[-1]

        e1_filename = get_filename_from_path(e1.text.strip())
        e2_filename = get_filename_from_path(e2.text.strip())

        if e1_filename != e2_filename:
            # ignore if its a directory name - mainly for logger
            if not os.path.isdir(e1.text):
                print(f'Different text at {path}: {e1.text} != {e2.text}')
                return False

    if (e1.tail or '').strip() != (e2.tail or '').strip():
        print(f"Different tail at {path}: {e1.tail} != {e2.tail}")
        return False
    if path != '' and path != '/sim' and e1.attrib != e2.attrib:  # Skip attribute check for top-level element
        print(f"Different attributes at {path}: {e1.attrib} != {e2.attrib}")
        return False
    if len(e1) != len(e2):
        e1children = []
        e2children = []
        for child in e1:
            e1children.append(child.tag)
        for child in e2:
            e2children.append(child.tag)
        print(f"Different number of children at {path}, solution has {e1children}, reference has {e2children}")
        return False
    return all(elements_equal(c1, c2, path=f"{path}/{c1.tag}") for c1, c2 in
               zip(sorted(e1, key=ET.tostring), sorted(e2, key=ET.tostring)))


class TestXML(unittest.TestCase):

    def test_multi(self):
        model = pj.Network("Variable")

        source = pj.Source(model, "source")

        queue = pj.Queue(model, "queue", pj.SchedStrategy.FCFS)

        sink = pj.Sink(model, "sink")

        jclass = pj.OpenClass(model, "class")

        source.setArrival(jclass, pj.Exp(0.5))

        queue.setService(jclass, pj.Exp(0.5))

        model.addLink(source, queue)

        model.addLink(queue, sink)

        model.printResults()

        queue2 = pj.Queue(model, "queue2", pj.SchedStrategy.FCFS)

        queue2.setService(jclass, pj.Erlang.fitMeanAndOrder(1, 2))

        queue.setService(jclass, pj.Exp(1))

        model.addLink(queue, queue2)

        model.addLink(queue2, sink)

        model.printResults()

        model.getResults()


    def test_Saving(self):
        # declare model
        model = pj.Network("M/M/1")

        # declare nodes
        source = pj.Source(model, "mySource")
        queue = pj.Queue(model, "myQueue", pj.SchedStrategy.FCFS)
        sink = pj.Sink(model, "mySink")

        # declare and set classes
        oclass = pj.OpenClass(model, "myClass")
        source.setArrival(oclass, pj.Exp(1))
        queue.setService(oclass, pj.Exp(2))

        # topology
        model.addLink(source, queue)
        model.addLink(queue, sink)

        # create solution file and open
        # model.jsimg_open()
        # model.saveTemp()
        model.saveResultsFileNamed("heyo", 1234)
        pj.printResultsFromResultsFile('heyo')
        map = pj.getResultsFromResultsFile("heyo")

        print("Opened ok")

    def test_MM1(self):
        # declare model
        model = pj.Network("M/M/1")

        # declare nodes
        source = pj.Source(model, "mySource")
        queue = pj.Queue(model, "myQueue", pj.SchedStrategy.FCFS)
        sink = pj.Sink(model, "mySink")

        # declare and set classes
        oclass = pj.OpenClass(model, "myClass")
        source.setArrival(oclass, pj.Exp(1))
        queue.setService(oclass, pj.Exp(2))

        # topology
        model.addLink(source, queue)
        model.addLink(queue, sink)

        # create solution file
        model.generate_xml('test_xml_solutions/test_mm1_solution.jsimg')

        # Parse the generated file and the reference file
        generated_tree = ET.parse('test_xml_solutions/test_mm1_solution.jsimg')
        reference_tree = ET.parse('test_xml_references/test_mm1_reference.jsimg')

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("M/M/1 Ok")

    def test_MG1(self):
        # declare model
        model = pj.Network("M/G/1")

        # declare nodes
        source = pj.Source(model, "Source")
        queue = pj.Queue(model, "Queue", pj.SchedStrategy.FCFS)
        sink = pj.Sink(model, "Sink")

        # declare and set classes
        jobclass1 = pj.OpenClass(model, 'Class1')
        jobclass2 = pj.OpenClass(model, 'Class2')
        source.setArrival(jobclass1, pj.Exp(0.5))
        source.setArrival(jobclass2, pj.Exp(0.5))

        queue.setService(jobclass1, pj.Erlang.fitMeanAndSCV(1, 1 / 3))
        queue.setService(jobclass2, pj.Replayer('example_trace.txt'))

        # topology
        model.addLink(source, queue)
        model.addLink(queue, sink)

        # create solution file
        model.generate_xml('test_xml_solutions/test_mg1_solution.jsimg')

        # Parse the generated file and the reference file
        generated_tree = ET.parse('test_xml_solutions/test_mg1_solution.jsimg')
        reference_tree = ET.parse('test_xml_references/test_mg1_reference.jsimg')

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("M/G/1 Ok")

    def test_MIP(self):
        # Machine interference problem example

        # declare model
        S = 2
        N = 3
        model = pj.Network('MIP')

        # declare nodes
        delay = pj.Delay(model, 'WorkingState')
        queue = pj.Queue(model, 'RepairQueue', pj.SchedStrategy.FCFS)
        queue.setNumberOfServers(S)

        # declare and set classes
        cclass = pj.ClosedClass(model, 'Machines', N, delay)
        delay.setService(cclass, pj.Exp(0.5))
        queue.setService(cclass, pj.Exp(4.0))

        # topology
        model.addLink(delay, queue)
        model.addLink(queue, delay)

        # create solution file
        model.generate_xml('test_xml_solutions/test_mip_solution.jsimg')

        # Parse the generated file and the reference file
        generated_tree = ET.parse('test_xml_solutions/test_mip_solution.jsimg')
        reference_tree = ET.parse('test_xml_references/test_mip_reference.jsimg')

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("MIP Ok")

    def test_RRLB(self):
        # Round robin load balancing example
        # declare model
        model = pj.Network('RRLB')

        # declare nodes
        source = pj.Source(model, 'Source')
        lb = pj.Router(model, 'LB')
        queue1 = pj.Queue(model, 'Queue1', pj.SchedStrategy.PS)
        queue2 = pj.Queue(model, 'Queue2', pj.SchedStrategy.PS)
        sink = pj.Sink(model, 'Sink')

        # declare and set classes
        oclass = pj.OpenClass(model, 'Class1')
        source.setArrival(oclass, pj.Exp(1))
        queue1.setService(oclass, pj.Exp(2))
        queue2.setService(oclass, pj.Exp(2))

        # topology
        model.addLinks([(source, lb),
                        (lb, queue1),
                        (lb, queue2),
                        (queue1, sink),
                        (queue2, sink)])

        lb.setRouting(oclass, pj.RoutingStrategy.RROBIN)

        # create solution file
        model.generate_xml('test_xml_solutions/test_rrlb_solution.jsimg')

        # Parse the generated file and the reference file
        generated_tree = ET.parse('test_xml_solutions/test_rrlb_solution.jsimg')
        reference_tree = ET.parse('test_xml_references/test_rrlb_reference.jsimg')

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("RRLB Ok")

    def test_ReentrantLine(self):
        # Reentrant Line modelling example

        # declare model
        model = pj.Network('test_reentantline_classswitch_routing')

        # declare nodes
        queue = pj.Queue(model, 'Queue_1', pj.SchedStrategy.FCFS, 3, pj.DropStrategy.WAITING_QUEUE)

        # declare and set classes
        K = 3
        N = [1, 0, 0]
        jobclass = [None] * K  # Initialize list of job classes
        for k in range(0, K):
            jobclass[k] = pj.ClosedClass(model, 'Class' + str(k + 1), N[k], queue)
            queue.setService(jobclass[k], pj.Erlang.fitMeanAndOrder(k + 1, 2))

        # topology
        queue.setRouting(jobclass[0], pj.RoutingStrategy.CLASSSWITCH)
        queue.setRouting(jobclass[1], pj.RoutingStrategy.CLASSSWITCH)
        queue.setRouting(jobclass[2], pj.RoutingStrategy.CLASSSWITCH)

        P = model.init_routing_matrix()

        P[(jobclass[0], jobclass[1])][(queue, queue)] = 1.0
        P[(jobclass[1], jobclass[2])][(queue, queue)] = 1.0
        P[(jobclass[2], jobclass[0])][(queue, queue)] = 1.0

        model.link(P)

        # create solution file
        model.generate_xml('test_xml_solutions/test_reentantline_classswitch_routing_solution.jsimg')

        # Parse the generated file and the reference file
        generated_tree = ET.parse('test_xml_solutions/test_reentantline_classswitch_routing_solution.jsimg')
        reference_tree = ET.parse('test_xml_references/test_reentantline_classswitch_routing_reference.jsimg')

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("ReentrantLine with classswitch routing Ok")

    def test_classSwitch(self):
        model = pj.Network('test_classSwitch')

        # declare nodes
        source1 = pj.Source(model, 'Source 1')
        source2 = pj.Source(model, 'Source 2')

        queue1 = pj.Queue(model, 'Queue 1', pj.SchedStrategy.FCFS)
        queue2 = pj.Queue(model, 'Queue 2', pj.SchedStrategy.FCFS)

        sink = pj.Sink(model, 'Sink 1')

        # declare and set classes
        class1 = pj.OpenClass(model, 'Class1')
        class2 = pj.OpenClass(model, 'Class2')

        # Create classswitches
        classswitch1 = pj.ClassSwitch(model, "ClassSwitch 1")
        classswitch2 = pj.ClassSwitch(model, "ClassSwitch 2")

        source1.setArrival(class1, pj.Exp(0.5))
        source2.setArrival(class2, pj.Exp(1))

        queue1.setService(class1, pj.Exp(1))
        queue1.setService(class2, pj.Exp(1))
        queue2.setService(class1, pj.Exp(1))
        queue2.setService(class2, pj.Exp(1))

        # Set some classswitch probabilites by hand

        classswitch1.setClassSwitchProb(class1, class1, 0.4)
        classswitch1.setClassSwitchProb(class1, class2, 0.6)
        classswitch1.setClassSwitchProb(class2, class1, 0.6)
        classswitch1.setClassSwitchProb(class2, class2, 0.4)

        classswitch2.setClassSwitchProb(class1, class1, 0.5)
        classswitch2.setClassSwitchProb(class1, class2, 0.5)
        classswitch2.setClassSwitchProb(class2, class1, 0.5)
        classswitch2.setClassSwitchProb(class2, class2, 0.5)

        # topology
        model.addLinks([(source1, queue1),
                        (source1, queue2),
                        (source2, queue1),
                        (source2, queue2),
                        (queue1, classswitch1),
                        (queue2, classswitch1),
                        (classswitch1, sink)])

        # create solution file
        model.generate_xml("test_xml_solutions/test_classSwitch_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse("test_xml_solutions/test_classSwitch_solution.jsimg")
        reference_tree = ET.parse("test_xml_references/test_classSwitch_reference.jsimg")

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("Classswitch Ok")

    def test_fork_join(self):
        model = pj.Network('test_fork_join')

        # declare nodes
        source1 = pj.Source(model, 'Source 1')

        fork = pj.Fork(model, 'Fork 1')
        fork.setTasksPerLink(2)

        queue1 = pj.Queue(model, 'Queue 1', pj.SchedStrategy.FCFS)
        queue2 = pj.Queue(model, 'Queue 2', pj.SchedStrategy.FCFS)
        delay1 = pj.Delay(model, 'Delay 1')

        join = pj.Join(model, "Join 1")

        sink = pj.Sink(model, 'Sink 1')

        # declare and set classes
        class1 = pj.OpenClass(model, 'Class1')

        source1.setArrival(class1, pj.Exp(0.5))

        queue1.setService(class1, pj.Exp(1))
        queue2.setService(class1, pj.Exp(1))
        delay1.setService(class1, pj.Exp(1))

        # topology
        model.addLinks([(source1, fork),
                        (fork, queue1),
                        (fork, delay1),
                        (delay1, queue2),
                        (queue1, join),
                        (queue2, join),
                        (join, sink)])

        # create solution file
        model.generate_xml("test_xml_solutions/test_fork_join_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse("test_xml_solutions/test_fork_join_solution.jsimg")
        reference_tree = ET.parse("test_xml_references/test_fork_join_reference.jsimg")

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("fork and join Ok")

    def test_logger_fcr(self):
        model = pj.Network('test_logger_fcr')

        # declare nodes
        source1 = pj.Source(model, 'mySource')

        myQueue = pj.Queue(model, 'myQueue', pj.SchedStrategy.FCFS)
        queue2 = pj.Queue(model, 'Queue 2', pj.SchedStrategy.FCFS)
        logger1 = pj.Logger(model, "Logger 1")

        sink = pj.Sink(model, 'mySink')

        # declare and set classes
        myClass = pj.OpenClass(model, 'myClass')
        class2 = pj.OpenClass(model, 'Class2')

        source1.setArrival(myClass, pj.Exp(1))
        source1.setArrival(class2, pj.Exp(0.5))

        myQueue.setService(myClass, pj.Exp(2))
        myQueue.setService(class2, pj.Exp(1))
        queue2.setService(myClass, pj.Exp(1))
        queue2.setService(class2, pj.Exp(1))

        fcr1 = pj.FiniteCapacityRegion(model, "FCRegion1", queue2)
        fcr2 = pj.FiniteCapacityRegion(model, "FCRegion2", myQueue)
        fcr1.setMaxCapacity(20)

        # topology
        model.addLinks([(source1, logger1),
                        (source1, myQueue),
                        (logger1, queue2),
                        (logger1, sink),
                        (myQueue, queue2),
                        (myQueue, sink),
                        (queue2, sink)])

        model.useDefaultMetrics(False)
        # create solution file
        model.generate_xml("test_xml_solutions/test_logger_fcr_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse("test_xml_solutions/test_logger_fcr_solution.jsimg")
        reference_tree = ET.parse("test_xml_references/test_logger_fcr_reference.jsimg")

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("logger and fcr Ok")

    def test_add_metrics(self):
        model = pj.Network('test_add_metric')

        # declare nodes
        source1 = pj.Source(model, 'Source 1')

        fork = pj.Fork(model, 'Fork 1')
        fork.setTasksPerLink(2)

        queue1 = pj.Queue(model, 'Queue 1', pj.SchedStrategy.FCFS)
        queue2 = pj.Queue(model, 'Queue 2', pj.SchedStrategy.FCFS)
        delay1 = pj.Delay(model, 'Delay 1')

        join = pj.Join(model, "Join 1")

        sink = pj.Sink(model, 'Sink 1')

        # declare and set classes
        class1 = pj.OpenClass(model, 'Class1')

        source1.setArrival(class1, pj.Exp(0.5))

        queue1.setService(class1, pj.Exp(1))
        queue2.setService(class1, pj.Exp(1))
        delay1.setService(class1, pj.Exp(1))

        # topology
        model.addLinks([(source1, fork),
                        (fork, queue1),
                        (fork, delay1),
                        (delay1, queue2),
                        (queue1, join),
                        (queue2, join),
                        (join, sink)])

        model.useDefaultMetrics(False)
        model.addMetric(class1, model, pj.Metrics.NUM_CUSTOMERS)
        model.addMetric(class1, queue1, pj.Metrics.QUEUE_TIME)
        model.addMetric(class1, queue2, pj.Metrics.RESPONSE_TIME)
        model.addMetric(class1, delay1, pj.Metrics.RESIDENCE_TIME)
        model.addMetric(class1, fork, pj.Metrics.ARRIVAL_RATE)
        model.addMetric(class1, join, pj.Metrics.THROUGHPUT)
        model.addMetric(class1, queue2, pj.Metrics.UTILIZATION)
        model.addMetric(class1, queue1, pj.Metrics.EFFECTIVE_UTILIZATION)
        model.addMetric(class1, queue2, pj.Metrics.DROP_RATE)
        model.addMetric(class1, queue1, pj.Metrics.BALKING_RATE)
        model.addMetric(class1, queue2, pj.Metrics.RENEGING_RATE)
        model.addMetric(class1, queue1, pj.Metrics.RETRIAL_RATE)
        model.addMetric(class1, queue2, pj.Metrics.RETRIAL_ORBIT_SIZE)
        model.addMetric(class1, queue1, pj.Metrics.RETRIAL_ORBIT_RESIDENCE_TIME)
        model.addMetric(class1, model, pj.Metrics.POWER)
        model.addMetric(class1, sink, pj.Metrics.RESPONSE_TIME_PER_SINK)
        model.addMetric(class1, sink, pj.Metrics.THROUGHPUT_PER_SINK)
        model.addMetric(class1, fork, pj.Metrics.FORK_JOIN_NUM_CUSTOMERS)
        model.addMetric(class1, fork, pj.Metrics.FORK_JOIN_RESPONSE_TIME)

        # model.generateResultsFileNamed("heyo", 1234)
        # model.printResultsFromFile('heyo')

        # create solution file
        model.generate_xml("test_xml_solutions/test_add_metrics_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse("test_xml_solutions/test_add_metrics_solution.jsimg")
        reference_tree = ET.parse("test_xml_references/test_add_metrics_reference.jsimg")

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("adding metrics Ok")

    def test_DistributionsLoadIndependent(self):
        # Distributions tested: Coxian, Deterministic, Erlang, Exponential, Gamma, Hyperexponential,
        # Lognormal, Normal, Pareto, Replayer, Uniform, Weibull

        model = pj.Network('DistributionsLoadIndepdent')

        # declare nodes
        source = pj.Source(model, 'Exp(1) Source')
        queue1 = pj.Queue(model, 'cox(1,0.125,0.875) Queue', pj.SchedStrategy.FCFS)
        queue2 = pj.Queue(model, 'det(1) Queue', pj.SchedStrategy.FCFS)
        queue3 = pj.Queue(model, 'erl(0.8,4) Queue', pj.SchedStrategy.FCFS)
        queue4 = pj.Queue(model, 'exp(1) Queue', pj.SchedStrategy.FCFS)
        queue5 = pj.Queue(model, 'gam(4,0.5) Queue', pj.SchedStrategy.FCFS)
        queue6 = pj.Queue(model, 'hyp(0.2,0.1,0.4) Queue', pj.SchedStrategy.FCFS)
        queue7 = pj.Queue(model, 'lognorm(-0.805, 1.269) Queue', pj.SchedStrategy.FCFS)
        queue8 = pj.Queue(model, 'norm(2,1) Queue', pj.SchedStrategy.FCFS)
        queue9 = pj.Queue(model, 'par(3,1) Queue', pj.SchedStrategy.FCFS)
        queue10 = pj.Queue(model, 'replayer(\'example_trace.txt\') Queue', pj.SchedStrategy.FCFS)
        queue11 = pj.Queue(model, 'U(0,1) Queue', pj.SchedStrategy.FCFS)
        queue12 = pj.Queue(model, 'weibull(0.445, 0.471) Queue', pj.SchedStrategy.FCFS)
        queue13 = pj.Queue(model, 'Disabled Queue', pj.SchedStrategy.FCFS)
        queue14 = pj.Queue(model, 'Zero Service Time Queue', pj.SchedStrategy.FCFS)
        sink = pj.Sink(model, 'Sink')
        # declare and set classes
        oclass = pj.OpenClass(model, 'Class1')
        source.setArrival(oclass, pj.Exp(1))
        queue1.setService(oclass, pj.Cox(1, 0.125, 0.875))
        queue2.setService(oclass, pj.Det(1))
        queue3.setService(oclass, pj.Erlang(0.8, 4))
        queue4.setService(oclass, pj.Exp(1))
        queue5.setService(oclass, pj.Gamma(4, 0.5))
        queue6.setService(oclass, pj.HyperExp(0.2, 0.1, 0.4))
        queue7.setService(oclass, pj.Lognormal(-0.805, 1.269))
        queue8.setService(oclass, pj.Normal(2, 1))
        queue9.setService(oclass, pj.Pareto(3, 1))
        queue10.setService(oclass, pj.Replayer('example_trace.txt'))
        queue11.setService(oclass, pj.Uniform(0, 1))
        queue12.setService(oclass, pj.Weibull(0.445, 0.471))
        queue13.setService(oclass, pj.Disabled())
        queue14.setService(oclass, pj.ZeroServiceTime())

        # topology
        model.addLinks([(source, queue13),
                        (source, queue14),
                        (source, queue1),
                        (queue13, queue1),
                        (queue14, queue1),
                        (queue1, queue2),
                        (queue2, queue3),
                        (queue3, queue4),
                        (queue4, queue5),
                        (queue5, queue6),
                        (queue6, queue7),
                        (queue7, queue8),
                        (queue8, queue9),
                        (queue9, queue10),
                        (queue10, queue11),
                        (queue11, queue12),
                        (queue12, sink)])

        # create solution file
        model.generate_xml("test_xml_solutions/test_DistributionsLoadIndependent_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse('test_xml_solutions/test_DistributionsLoadIndependent_solution.jsimg')
        reference_tree = ET.parse('test_xml_references/test_DistributionsLoadIndependent_reference.jsimg')

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("Distributions Ok")

    def test_SchedulingStrategies_NPE_PE_PS(self):
        # Distributions tested: Coxian, Deterministic, Erlang, Exponential, Gamma, Hyperexponential,
        # Lognormal, Normal, Pareto, Replayer, Uniform, Weibull

        # Scheduling Strategies tested: Non-preemptive: FCFS, LCFS, RAND, SJF, LJF, SEPT, LEPT
        # Preemptive: FCFS-PR, LCFS-PR, SRPT
        # Processor Sharing: PS, DPS, GPS
        model = pj.Network('test_SchedulingStrategies_NPE_PE_PS')

        # declare nodes
        source = pj.Source(model, 'Exp(1) Source')
        queue1 = pj.Queue(model, 'cox(1,0.125,0.875) FCFS Queue', pj.SchedStrategy.FCFS)
        queue2 = pj.Queue(model, 'det(1) LCFS Queue', pj.SchedStrategy.LCFS)
        queue3 = pj.Queue(model, 'erl(0.8,4) RAND Queue', pj.SchedStrategy.RAND)
        queue4 = pj.Queue(model, 'exp(1) SJF Queue', pj.SchedStrategy.SJF)
        queue5 = pj.Queue(model, 'gam(4,0.5) LJF Queue', pj.SchedStrategy.LJF)
        queue6 = pj.Queue(model, 'hyp(0.2,0.1,0.4) SEPT Queue', pj.SchedStrategy.SEPT)
        queue7 = pj.Queue(model, 'lognorm(-0.805, 1.269) LEPT Queue', pj.SchedStrategy.LEPT)
        queue8 = pj.Queue(model, 'norm(2,1) FCFS-PR Queue', pj.SchedStrategy.FCFS_PR)
        queue9 = pj.Queue(model, 'par(3,1) LCFS-PR Queue', pj.SchedStrategy.LCFS_PR)
        queue10 = pj.Queue(model, 'replayer(\'example_trace.txt\') SRPT Queue', pj.SchedStrategy.SRPT)
        queue11 = pj.Queue(model, 'U(0,1) PS Queue', pj.SchedStrategy.PS)
        queue12 = pj.Queue(model, 'weibull(0.445, 0.471) DPS Queue', pj.SchedStrategy.DPS)
        queue13 = pj.Queue(model, 'weibull(0.445, 0.471) GPS Queue', pj.SchedStrategy.GPS)
        sink = pj.Sink(model, 'Sink')

        # declare and set classes
        oclass = pj.OpenClass(model, 'Class1')
        source.setArrival(oclass, pj.Exp(1))
        queue1.setService(oclass, pj.Cox(1, 0.125, 0.875))
        queue2.setService(oclass, pj.Det(1))
        queue3.setService(oclass, pj.Erlang(0.8, 4))
        queue4.setService(oclass, pj.Exp(1))
        queue5.setService(oclass, pj.Gamma(4, 0.5))
        queue6.setService(oclass, pj.HyperExp(0.2, 0.1, 0.4))
        queue7.setService(oclass, pj.Lognormal(-0.805, 1.269))
        queue8.setService(oclass, pj.Normal(2, 1))
        queue9.setService(oclass, pj.Pareto(3, 1))
        queue10.setService(oclass, pj.Replayer('example_trace.txt'))
        queue11.setService(oclass, pj.Uniform(0, 1))
        queue12.setService(oclass, pj.Weibull(0.445, 0.471))
        queue13.setService(oclass, pj.Weibull(0.445, 0.471))

        # topology
        model.addLinks([(source, queue1),
                        (queue1, queue2),
                        (queue2, queue3),
                        (queue3, queue4),
                        (queue4, queue5),
                        (queue5, queue6),
                        (queue6, queue7),
                        (queue7, queue8),
                        (queue8, queue9),
                        (queue9, queue10),
                        (queue10, queue11),
                        (queue11, queue12),
                        (queue12, queue13),
                        (queue13, sink)])

        # create solution file
        model.generate_xml("test_xml_solutions/test_SchedulingStrategies_NPE_PE_PS_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse('test_xml_solutions/test_SchedulingStrategies_NPE_PE_PS_solution.jsimg')
        reference_tree = ET.parse('test_xml_references/test_SchedulingStrategies_NPE_PE_PS_reference.jsimg')

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("SchedulingStrategies NPE PE PS Ok")

    def test_SchedulingStrategies_Priority_NPE_PE(self):
        # Distributions tested: Coxian, Deterministic, Erlang, Exponential, Gamma, Hyperexponential,
        # Lognormal, Normal, Pareto, Replayer

        # Scheduling Strategies tested: Non-preemptive: FCFS_PRIORITY, LCFS_PRIORITY, RAND_PRIORITY,
        # SJF_PRIORITY, LJF_PRIORITY, SEPT_PRIORITY, LEPT_PRIORITY
        # Preemptive: FCFS-PR_PRIORITY, LCFS-PR_PRIORITY, SRPT_PRIORITY

        model = pj.Network('test_SchedulingStrategies_NPE_PE_PS')

        # declare nodes
        source = pj.Source(model, 'Exp(1) Source')
        queue1 = pj.Queue(model, 'cox(1,0.125,0.875) FCFS Queue', pj.SchedStrategy.FCFS_PRIORITY)
        queue2 = pj.Queue(model, 'det(1) LCFS Queue', pj.SchedStrategy.LCFS_PRIORITY)
        queue3 = pj.Queue(model, 'erl(0.8,4) RAND Queue', pj.SchedStrategy.RAND_PRIORITY)
        queue4 = pj.Queue(model, 'exp(1) SJF Queue', pj.SchedStrategy.SJF_PRIORITY)
        queue5 = pj.Queue(model, 'gam(4,0.5) LJF Queue', pj.SchedStrategy.LJF_PRIORITY)
        queue6 = pj.Queue(model, 'hyp(0.2,0.1,0.4) SEPT Queue', pj.SchedStrategy.SEPT_PRIORITY)
        queue7 = pj.Queue(model, 'lognorm(-0.805, 1.269) LEPT Queue', pj.SchedStrategy.LEPT_PRIORITY)
        queue8 = pj.Queue(model, 'norm(2,1) FCFS-PR Queue', pj.SchedStrategy.FCFS_PR_PRIORITY)
        queue9 = pj.Queue(model, 'par(3,1) LCFS-PR Queue', pj.SchedStrategy.LCFS_PR_PRIORITY)
        queue10 = pj.Queue(model, 'replayer(\'example_trace.txt\') SRPT Queue', pj.SchedStrategy.SRPT_PRIORITY)
        sink = pj.Sink(model, 'Sink')

        # declare and set classes
        oclass = pj.OpenClass(model, 'Class1')
        source.setArrival(oclass, pj.Exp(1))
        queue1.setService(oclass, pj.Cox(1, 0.125, 0.875))
        queue2.setService(oclass, pj.Det(1))
        queue3.setService(oclass, pj.Erlang(0.8, 4))
        queue4.setService(oclass, pj.Exp(1))
        queue5.setService(oclass, pj.Gamma(4, 0.5))
        queue6.setService(oclass, pj.HyperExp(0.2, 0.1, 0.4))
        queue7.setService(oclass, pj.Lognormal(-0.805, 1.269))
        queue8.setService(oclass, pj.Normal(2, 1))
        queue9.setService(oclass, pj.Pareto(3, 1))
        queue10.setService(oclass, pj.Replayer('example_trace.txt'))

        # topology
        model.addLinks([(source, queue1),
                        (queue1, queue2),
                        (queue2, queue3),
                        (queue3, queue4),
                        (queue4, queue5),
                        (queue5, queue6),
                        (queue6, queue7),
                        (queue7, queue8),
                        (queue8, queue9),
                        (queue9, queue10),
                        (queue10, sink)])

        # create solution file
        model.generate_xml("test_xml_solutions/test_SchedulingStrategies_Priority_NPE_PE_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse("test_xml_solutions/test_SchedulingStrategies_Priority_NPE_PE_solution.jsimg")
        reference_tree = ET.parse("test_xml_references/test_SchedulingStrategies_Priority_NPE_PE_reference.jsimg")

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("SchedulingStrategies Priority NPE PE Ok")

    def test_RoutingStrategies_Static(self):
        # Routing Strategies tested: Random, Round Robin, JSQ, Shortest response time,
        # least utilization, fastest service time, disabled

        model = pj.Network('test_RoutingStrategies_Static')

        # declare nodes
        source = pj.Source(model, 'Random Source')
        queue1 = pj.Queue(model, 'Round Robin Queue', pj.SchedStrategy.FCFS)
        queue2 = pj.Queue(model, 'JSQ Queue', pj.SchedStrategy.FCFS)
        queue3 = pj.Queue(model, 'Shortest response time Queue', pj.SchedStrategy.FCFS)
        queue4 = pj.Queue(model, 'Least Utilization Queue', pj.SchedStrategy.FCFS)
        queue5 = pj.Queue(model, 'Fastest Service Queue', pj.SchedStrategy.FCFS)
        queue6 = pj.Queue(model, 'Disabled Queue', pj.SchedStrategy.FCFS)
        sink = pj.Sink(model, 'Sink')

        # declare and set classes
        oclass = pj.OpenClass(model, 'Class1')
        source.setArrival(oclass, pj.Exp(0.5))
        queue1.setService(oclass, pj.Exp(1))
        queue2.setService(oclass, pj.Exp(1))
        queue3.setService(oclass, pj.Exp(1))
        queue4.setService(oclass, pj.Exp(1))
        queue5.setService(oclass, pj.Exp(1))
        queue6.setService(oclass, pj.Exp(1))

        source.setRouting(oclass, pj.RoutingStrategy.RANDOM)
        queue1.setRouting(oclass, pj.RoutingStrategy.RROBIN)
        queue2.setRouting(oclass, pj.RoutingStrategy.JSQ)
        queue3.setRouting(oclass, pj.RoutingStrategy.SHORTEST_RESPONSE_TIME)
        queue4.setRouting(oclass, pj.RoutingStrategy.LEAST_UTILIZATION)
        queue5.setRouting(oclass, pj.RoutingStrategy.FASTEST_SERVICE)
        queue6.setRouting(oclass, pj.RoutingStrategy.DISABLED)

        # topology
        model.addLinks([(source, queue1),
                        (queue1, queue2),
                        (queue2, queue3),
                        (queue3, queue4),
                        (queue4, queue5),
                        (queue5, queue6),
                        (queue6, sink)])

        # create solution file
        model.generate_xml("test_xml_solutions/test_RoutingStrategies_Static_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse("test_xml_solutions/test_RoutingStrategies_Static_solution.jsimg")
        reference_tree = ET.parse("test_xml_references/test_RoutingStrategies_Static_reference.jsimg")

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("Routing Strategies Static Ok")

    def test_RoutingStrategies_Probabilities(self):
        # Routing Strategies tested: Random, Round Robin, Probabilities

        model = pj.Network('test_RoutingStrategies_Probabilites')

        # declare nodes
        source = pj.Source(model, 'Source Q1 0.2 Q2 0.4 Q3 0.4')
        queue1 = pj.Queue(model, 'Queue 1 Random', pj.SchedStrategy.FCFS)
        queue2 = pj.Queue(model, 'Queue 2 Q4 0.6 Q5 0.4', pj.SchedStrategy.FCFS)
        queue3 = pj.Queue(model, 'Queue 2 RRobin', pj.SchedStrategy.FCFS)
        queue4 = pj.Queue(model, 'Queue 4 Random', pj.SchedStrategy.FCFS)
        queue5 = pj.Queue(model, 'Queue 5 Q5 0.7 Sink 0.3', pj.SchedStrategy.FCFS)
        sink = pj.Sink(model, 'Sink 1')

        # declare and set classes
        oclass = pj.OpenClass(model, 'Class1')
        source.setArrival(oclass, pj.Exp(0.5))
        queue1.setService(oclass, pj.Exp(1))
        queue2.setService(oclass, pj.Exp(1))
        queue3.setService(oclass, pj.Exp(1))
        queue4.setService(oclass, pj.Exp(1))
        queue5.setService(oclass, pj.Exp(1))

        source.setRouting(oclass, pj.RoutingStrategy.PROB)
        queue1.setRouting(oclass, pj.RoutingStrategy.RANDOM)
        queue2.setRouting(oclass, pj.RoutingStrategy.PROB)
        queue3.setRouting(oclass, pj.RoutingStrategy.RROBIN)
        queue4.setRouting(oclass, pj.RoutingStrategy.RANDOM)
        queue5.setRouting(oclass, pj.RoutingStrategy.PROB)

        source.setProbRouting(oclass, queue1, 0.2)
        source.setProbRouting(oclass, queue2, 0.4)
        source.setProbRouting(oclass, queue3, 0.4)
        queue2.setProbRouting(oclass, queue4, 0.6)
        queue2.setProbRouting(oclass, queue5, 0.4)
        queue5.setProbRouting(oclass, queue5, 0.7)
        queue5.setProbRouting(oclass, sink, 0.3)

        # topology
        model.addLinks([(source, queue1),
                        (source, queue2),
                        (source, queue3),
                        (queue1, queue4),
                        (queue1, queue5),
                        (queue2, queue4),
                        (queue2, queue5),
                        (queue3, queue4),
                        (queue3, queue5),
                        (queue5, queue5),
                        (queue5, sink),
                        (queue4, sink)])

        # create solution file
        model.generate_xml("test_xml_solutions/test_RoutingStrategies_Probabilities_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse("test_xml_solutions/test_RoutingStrategies_Probabilities_solution.jsimg")
        reference_tree = ET.parse("test_xml_references/test_RoutingStrategies_Probabilities_reference.jsimg")

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("Routing Strategies Probabilities Ok")


if __name__ == '__main__':
    unittest.main()
