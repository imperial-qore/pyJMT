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
        if not (os.path.isfile(e1.text.strip()) and os.path.isfile(e2.text.strip())):
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
    return all(elements_equal(c1, c2, path=f"{path}/{c1.tag}") for c1, c2 in zip(sorted(e1, key=ET.tostring), sorted(e2, key=ET.tostring)))


class TestXML(unittest.TestCase):

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
        model.link(source, queue)
        model.link(queue, sink)

        # create solution file
        model.generate_xml("testmm1_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse('testmm1_solution.jsimg')
        reference_tree = ET.parse('testmm1_reference.jsimg')

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

        queue.setService(jobclass1, pj.Erlang.fitMeanAndSCV(1, 1/3))
        queue.setService(jobclass2, pj.Replayer('example_trace.txt'))

        # topology
        model.link(source, queue)
        model.link(queue, sink)

        # create solution file
        model.generate_xml("testmg1_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse('testmg1_solution.jsimg')
        reference_tree = ET.parse('testmg1_reference.jsimg')

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
        #TODO CHECK HOW LINKING SHOULD WORK
        model.link(delay, queue)
        model.link(queue, delay)

        # create solution file
        model.generate_xml("testmip_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse('testmip_solution.jsimg')
        reference_tree = ET.parse('testmip_reference.jsimg')

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("MIP Ok")

    def test_RRLB(self):
        # Round robin load balancing example
        # declare model
        model = pj.Network('RRLB');

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
        #TODO CHECK HOW LINKING SHOULD WORK
        model.addLinks([(source, lb),
                        (lb, queue1),
                        (lb, queue2),
                        (queue1, sink),
                        (queue2, sink)])

        lb.setRouting(oclass, pj.RoutingStrategy.RROBIN)

        # create solution file
        model.generate_xml("testrrlb_solution.jsimg")

        # Parse the generated file and the reference file
        generated_tree = ET.parse('testrrlb_solution.jsimg')
        reference_tree = ET.parse('testrrlb_reference.jsimg')

        # Compare the generated file with the reference file
        self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
        print("RRLB Ok")

    # def test_ReentrantLine(self):
    #     # Reentrant Line modelling example
    #
    #     # declare model
    #     model = pj.Network('RL')
    #
    #     # declare nodes
    #     queue = pj.Queue(model, 'Queue', pj.SchedStrategy.FCFS)
    #
    #     # declare and set classes
    #     K = 3
    #     N = [1, 0, 0]
    #     jobclass = [None] * K  # Initialize list of job classes
    #     for k in range(0, K):
    #         jobclass[k] = pj.ClosedClass(model, 'Class' + str(k + 1), N[k], queue)
    #         queue.setService(jobclass[k], pj.Erlang.fitMeanAndOrder(k + 1, 2))
    #
    #     # topology
    #
    #     P = model.init_routing_matrix()
    #
    #     # Assuming queue is an index, in Python we start indexing from 0
    #     P[jobclass[0]][jobclass[1]][queue][queue] = 1.0
    #     P[jobclass[1]][jobclass[2]][queue][queue] = 1.0
    #     P[jobclass[2]][jobclass[0]][queue][queue] = 1.0
    #
    #     model.link(P)
    #
    #     # create solution file
    #     model.generate_xml("testreentantline_solution.jsimg")
    #
    #     # Parse the generated file and the reference file
    #     generated_tree = ET.parse('testreetrantline_solution.jsimg')
    #     reference_tree = ET.parse('testreentantline_reference.jsimg')
    #
    #     # Compare the generated file with the reference file
    #     self.assertTrue(elements_equal(generated_tree.getroot(), reference_tree.getroot()))
    #     print("ReentrantLine Ok")


if __name__ == '__main__':
    unittest.main()
