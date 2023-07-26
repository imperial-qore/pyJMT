import pyJMT as pj

def test():
    model = pj.Network("test")
    source = pj.Source(model, "source")
    queue = pj.Queue(model, "queue", pj.SchedStrategy.FCFS)
    sink = pj.Sink(model, "sink")

    oclass = pj.OpenClass(model, "oclass")
    queue.setService(oclass, pj.Exp(0.5))
    source.setArrival(oclass, pj.Exp(1))

    model.addLinks([(source, queue), (queue, sink)])
    model.printResults()



if __name__ == '__main__':
    test()