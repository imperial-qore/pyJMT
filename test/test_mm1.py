import unittest
from pyJMT.network import Network, Source, Queue, Sink, OpenClass, Exponential, SchedStrategy
import xml.etree.ElementTree as ET


def elements_equal(e1, e2):
    if e1.tag != e2.tag: return False
    # ignore attrib for now as there are differences in timestamp and name that are unavoidable
    # if e1.attrib != e2.attrib: return False
    if (e1.text or '').strip() != (e2.text or '').strip(): return False
    if (e1.tail or '').strip() != (e2.tail or '').strip(): return False
    if len(e1) != len(e2): return False
    return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

class TestMM1(unittest.TestCase):

    def test_MM1(self):
        # declare model
        model = Network("M/M/1")

        # declare nodes
        source = Source(model, "mySource")
        queue = Queue(model, "myQueue", SchedStrategy.FCFS)
        sink = Sink(model, "mySink")

        # declare and set classes
        oclass = OpenClass(model, "myClass")
        source.setArrival(oclass, Exponential(1))
        queue.setService(oclass, Exponential(2))

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


if __name__ == '__main__':
    unittest.main()
