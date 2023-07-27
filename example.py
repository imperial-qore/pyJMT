import pyJMT as pj

def example_classes():
    model = pj.Network("test")
    source = pj.Source(model, "source")
    queue = pj.Queue(model, "queue", pj.SchedStrategy.FCFS)
    sink = pj.Sink(model, "sink")

    # An open class with priority of 2
    openclass = pj.OpenClass(model, "open class", 2)

    # A closed class with population of 10 originating from queue with a default priority (0)
    closedclass = pj.ClosedClass(model, "closed class", 10, queue)

    source.setArrival(openclass, pj.Exp(1))


import pyJMT as pj

def example_linking():
    # Basic model
    model = pj.Network("linking")
    source = pj.Source(model, "source")
    queue = pj.Queue(model, "queue", pj.SchedStrategy.FCFS)
    sink = pj.Sink(model, "sink")

    openclass = pj.OpenClass(model, "open class")
    source.setArrival(openclass, pj.Exp(1))
    queue.setService(openclass, pj.Exp(1))

    # Add serial linking from source to sink through queue
    model.addLink(source, queue)
    model.addLink(queue, sink)

    # Remove linking added above
    model.removeLink(source, queue)
    model.removeLink(queue, sink)

    # Add links back in one line
    model.addLinks([(source, queue), (queue, sink)])
    # Remove links again in one line
    model.removeLinks([(source, queue), (queue, sink)])


import pyJMT as pj

def example_routing():
    # Basic model with links
    model = pj.Network("test")
    source = pj.Source(model, "source")
    queue = pj.Queue(model, "queue", pj.SchedStrategy.FCFS)
    sink = pj.Sink(model, "sink")

    openclass1 = pj.OpenClass(model, "open class 1")
    openclass2 = pj.OpenClass(model, "open class 2")

    source.setArrival(openclass1, pj.Exp(1))
    source.setArrival(openclass2, pj.Exp(1))
    queue.setService(openclass1, pj.Exp(1))
    queue.setService(openclass2, pj.ZeroServiceTime())

    model.addLinks([(source, queue), (queue, sink), (queue, queue)])

    # Class 1 jobs have 100 percent chance of going to queue
    source.setRouting(openclass1, pj.RoutingStrategy.PROB)
    source.setProbRouting(openclass1, queue, 1.0)

    # Jobs of class 1 change to class 2 half the time and return to start of queue,
    # The other half of the time they continue to the sink as class 1 jobs
    queue.setRouting(openclass1, pj.RoutingStrategy.CLASSSWITCH)
    queue.setClassSwitchRouting(openclass1, openclass2, queue, 0.5, 1.0)
    queue.setClassSwitchRouting(openclass1, openclass1, sink, 0.5, 1.0)

    # Jobs of class 2 go to queue or sink in a round robin strategy
    queue.setRouting(openclass2, pj.RoutingStrategy.RROBIN)

import pyJMT as pj

def example_services():
    # Basic model with links
    model = pj.Network("example services")
    source = pj.Source(model, "source")
    queue = pj.Queue(model, "queue", pj.SchedStrategy.FCFS)
    sink = pj.Sink(model, "sink")

    openclass1 = pj.OpenClass(model, "open class 1")
    openclass2 = pj.OpenClass(model, "open class 2")

    source.setArrival(openclass1, pj.Cox(1.0, 2.0, 3.0))
    source.setArrival(openclass2, pj.Exp(1))
    queue.setService(openclass1, pj.Normal(2.0, 1.0))
    queue.setService(openclass2, pj.ZeroServiceTime())

    model.addLinks([(source, queue), (queue, sink), (queue, queue)])



if __name__ == '__main__':
    example_services()


