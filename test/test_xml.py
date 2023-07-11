import os
import unittest
from pyJMT.network import Network, Source, Queue, Delay, Sink, OpenClass, ClosedClass, Exp, Erlang, Replayer, SchedStrategy
import xml.etree.ElementTree as ET

def elements_equal(e1, e2, path=''):
    if e1.tag != e2.tag:
        print(f"Different tag at {path}: {e1.tag} != {e2.tag}")
        return False
    if e1.text != None and e2.text != None:
        if os.path.basename(e1.text) != os.path.basename(e2.text):
            print(f'Different text {e1.text} != {e2.text}')
            return False
    if (e1.tail or '').strip() != (e2.tail or '').strip():
        print(f"Different tail at {path}: {e1.tail} != {e2.tail}")
        return False
    # Ignore attributes for now as timestamp and file name will be different
    # if e1.attrib != e2.attrib:
    #     print(f"Different attributes at {path}: {e1.attrib} != {e2.attrib}")
    #     return False
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
        model = Network("M/M/1")

        # declare nodes
        source = Source(model, "mySource")
        queue = Queue(model, "myQueue", SchedStrategy.FCFS)
        sink = Sink(model, "mySink")

        # declare and set classes
        oclass = OpenClass(model, "myClass")
        source.setArrival(oclass, Exp(1))
        queue.setService(oclass, Exp(2))

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
        model = Network("M/G/1")

        # declare nodes
        source = Source(model, "Source")
        queue = Queue(model, "Queue", SchedStrategy.FCFS)
        sink = Sink(model, "Sink")

        # declare and set classes
        jobclass1 = OpenClass(model, 'Class1')
        jobclass2 = OpenClass(model, 'Class2')
        source.setArrival(jobclass1, Exp(0.5))
        source.setArrival(jobclass2, Exp(0.5))

        queue.setService(jobclass1, Erlang.fitMeanAndSCV(1, 1/3))
        queue.setService(jobclass2, Replayer('example_trace.txt'))

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
        # declare model
        S = 2
        N = 3
        model = Network('MIP')

        # declare nodes
        delay = Delay(model, 'WorkingState')
        queue = Queue(model, 'RepairQueue', SchedStrategy.FCFS)
        queue.setNumberOfServers(S)

        # declare and set classes
        cclass = ClosedClass(model, 'Machines', N, delay)
        delay.setService(cclass, Exp(0.5))
        queue.setService(cclass, Exp(4.0))

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

if __name__ == '__main__':
    unittest.main()
