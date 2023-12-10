import pyJMT as jmt

def example_classes():
    model = jmt.Network("example classes")
    source = jmt.Source(model, "source")
    queue = jmt.Queue(model, "queue", jmt.SchedStrategy.FCFS)
    sink = jmt.Sink(model, "sink")

    # An open class with priority of 2
    openclass = jmt.OpenClass(model, "open class", 2)

    # A closed class with population of 10 originating from queue with a default priority (0)
    closedclass = jmt.ClosedClass(model, "closed class", 10, queue)

    source.setArrival(openclass, jmt.Exp(1))

    # Open the model
    model.jsimgOpen()


def example_linking():
    # Basic model
    model = jmt.Network("linking")
    source = jmt.Source(model, "source")
    queue = jmt.Queue(model, "queue", jmt.SchedStrategy.FCFS)
    sink = jmt.Sink(model, "sink")

    openclass = jmt.OpenClass(model, "open class")
    source.setArrival(openclass, jmt.Exp(1))
    queue.setService(openclass, jmt.Exp(1))

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

    # Open the model
    model.jsimgOpen()

def example_services():
    # Basic model with links
    model = jmt.Network("example services")
    source = jmt.Source(model, "source")
    queue = jmt.Queue(model, "queue", jmt.SchedStrategy.FCFS)
    sink = jmt.Sink(model, "sink")

    openclass1 = jmt.OpenClass(model, "open class 1")
    openclass2 = jmt.OpenClass(model, "open class 2")

    source.setArrival(openclass1, jmt.Cox(1.0, 2.0, 0.5))
    source.setArrival(openclass2, jmt.Exp(1))
    queue.setService(openclass1, jmt.Normal(2.0, 1.0))
    queue.setService(openclass2, jmt.ZeroServiceTime())
    queue.setNumberOfServers(3)

    model.addLinks([(source, queue), (queue, sink), (queue, queue)])

    # Open the model
    model.jsimgOpen()

def example_routing():
    # Basic model with links
    model = jmt.Network("routing")
    source = jmt.Source(model, "source")
    queue = jmt.Queue(model, "queue", jmt.SchedStrategy.FCFS)
    sink = jmt.Sink(model, "sink")

    openclass1 = jmt.OpenClass(model, "open class 1")
    openclass2 = jmt.OpenClass(model, "open class 2")

    source.setArrival(openclass1, jmt.Exp(1))
    source.setArrival(openclass2, jmt.Exp(1))
    queue.setService(openclass1, jmt.Exp(1))
    queue.setService(openclass2, jmt.ZeroServiceTime())

    model.addLinks([(source, queue), (queue, sink), (queue, queue)])

    # Class 1 jobs have 100 percent chance of going to queue
    source.setRouting(openclass1, jmt.RoutingStrategy.PROB)
    source.setProbRouting(openclass1, queue, 1.0)

    # Jobs of class 1 change to class 2 half the time and return to start of queue,
    # The other half of the time they continue to the sink as class 1 jobs
    queue.setRouting(openclass1, jmt.RoutingStrategy.CLASSSWITCH)
    queue.setClassSwitchRouting(openclass1, openclass2, queue, 0.5, 1.0)
    queue.setClassSwitchRouting(openclass1, openclass1, sink, 0.5, 1.0)

    # Jobs of class 2 go to queue or sink in a round robin strategy
    queue.setRouting(openclass2, jmt.RoutingStrategy.RROBIN)

    # Open the model
    model.jsimgOpen()


def example_queues():
    # Basic model with links
    model = jmt.Network("example services")
    source = jmt.Source(model, "source")
    queue = jmt.Queue(model, "queue", jmt.SchedStrategy.FCFS)
    sink = jmt.Sink(model, "sink")

    openclass1 = jmt.OpenClass(model, "open class 1")
    openclass2 = jmt.OpenClass(model, "open class 2")

    source.setArrival(openclass1, jmt.Cox(1.0, 2.0, 0.5))
    source.setArrival(openclass2, jmt.Exp(1))
    queue.setService(openclass1, jmt.Normal(2.0, 1.0))
    queue.setService(openclass2, jmt.ZeroServiceTime())
    queue.setNumberOfServers(3)

    # Set additional queue parameters
    queue.setStrategy(jmt.SchedStrategy.FCFS_PRIORITY)
    queue.setCapacity(10)
    queue.setDropRule(jmt.DropStrategy.WAITING_QUEUE)

    model.addLinks([(source, queue), (queue, sink)])

    # Open the model
    model.jsimgOpen()

def example_forksjoins():
    # Basic model with links
    model = jmt.Network("example forks and joins")
    source = jmt.Source(model, "source")
    queue1 = jmt.Queue(model, "queue 1", jmt.SchedStrategy.FCFS)
    queue2 = jmt.Queue(model, "queue 2", jmt.SchedStrategy.FCFS)
    fork = jmt.Fork(model, "fork")
    join = jmt.Join(model, "join")
    sink = jmt.Sink(model, "sink")

    openclass1 = jmt.OpenClass(model, "open class 1")

    source.setArrival(openclass1, jmt.Cox(1.0, 2.0, 0.5))
    queue1.setService(openclass1, jmt.Normal(2.0, 1.0))
    queue1.setNumberOfServers(3)
    queue2.setService(openclass1, jmt.Exp(1.0))
    queue2.setNumberOfServers(2)

    fork.setTasksPerLink(1)
    model.addLinks([(source, fork), (fork, queue1), (fork, queue2),
                    (queue1, join), (queue2, join), (join, sink)])

    # Open the model
    model.jsimgOpen()


def example_metrics():
    # Basic model with links
    model = jmt.Network("example metrics")
    source = jmt.Source(model, "source")
    queue = jmt.Queue(model, "queue", jmt.SchedStrategy.FCFS)
    sink = jmt.Sink(model, "sink")

    openclass1 = jmt.OpenClass(model, "open class 1")
    openclass2 = jmt.OpenClass(model, "open class 2")

    source.setArrival(openclass1, jmt.Cox(1.0, 2.0, 0.5))
    source.setArrival(openclass2, jmt.Exp(1))
    queue.setService(openclass1, jmt.Normal(2.0, 1.0))
    queue.setService(openclass2, jmt.ZeroServiceTime())
    queue.setNumberOfServers(3)

    model.addLinks([(source, queue), (queue, sink), (queue, queue)])

    # Switch off default metrics
    model.useDefaultMetrics(False)
    # Add total customers metric to whole system for class 1
    model.addMetric(openclass1, model, jmt.Metrics.NUM_CUSTOMERS)
    # Add response time metric to queue for class 2
    model.addMetric(openclass2, queue, jmt.Metrics.RESPONSE_TIME)

    # Open the model
    model.jsimgOpen()

def example_saveandload():
    # Basic model with links
    model = jmt.Network("example save and load")
    source = jmt.Source(model, "source")
    queue = jmt.Queue(model, "queue", jmt.SchedStrategy.FCFS)
    sink = jmt.Sink(model, "sink")

    openclass1 = jmt.OpenClass(model, "open class 1")
    openclass2 = jmt.OpenClass(model, "open class 2")

    source.setArrival(openclass1, jmt.Cox(1.0, 2.0, 0.5))
    source.setArrival(openclass2, jmt.Exp(1))
    queue.setService(openclass1, jmt.Normal(2.0, 1.0))
    queue.setService(openclass2, jmt.ZeroServiceTime())
    queue.setNumberOfServers(3)

    model.addLinks([(source, queue), (queue, sink), (queue, queue)])

    # NOTE: ALL SAVED FILES GO TO ./output_files
    # save the current model as a .jsimg (can be opened in JMT)
    model.saveNamedJsimg("model")
    # generate a results file (.jsim) from the current model called "model"
    # (does not require a saved JSIMG first)
    model.saveResultsFileNamed("modelResults")
    # print the results from the current model
    # (does not require a saved results file beforehand)
    model.printResults()
    # return a dictionary of the results from the current model
    # (does not require saving)
    results_dict = model.getResults()

    # generate a results file from a .jsimg called "model"
    jmt.saveResultsFromJsimgFile("modelResults")
    # print the results from a results file (.jsim) called "model"
    # (does not require a saved results file beforehand)
    jmt.printResultsFromResultsFile("modelResults")
    # return a dictionary of the results from a results file called "model"
    results_dict = jmt.getResultsFromResultsFile("modelResults")

    # Open the model
    model.jsimgOpen()

