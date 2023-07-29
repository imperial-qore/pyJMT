import pyJMT as jmt

def example_mm1():
    model = jmt.Network("M/M/1 model")
    source = jmt.Source(model, "mySource")
    queue = jmt.Queue(model, "myQueue", jmt.SchedStrategy.FCFS)
    sink = jmt.Sink(model, "mySink")

    # An open class with priority of 2
    openclass = jmt.OpenClass(model, "Class1", 2)
    source.setArrival(openclass, jmt.Exp(0.5))
    queue.setService(openclass, jmt.Exp(1.0))

    model.addLink(source, queue)
    model.addLink(queue, sink)

    model.saveNamedJsimg("mm1")
    model.saveResultsFileNamed("mm1")
    model.printResults()
    print("The simulation result file is available under output_files/")

if __name__ == "__main__":
    example_mm1()
