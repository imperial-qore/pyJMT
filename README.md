# pyJMT
The pyJMT package is the official python wrapper for the [Java Modelling Tools](https://jmt.sf.net/) (JMT) suite, which is used for performance evaluation of systems using queueing network models. Using this tool the user can run JSIMgraph simulations in python, retrieving results programmatically.

# Documentation
A short getting started guide along with installation instructions can be found [here](https://github.com/imperial-qore/pyJMT/blob/main/pyJMT_manual.pdf), with full documentation available [here](https://imperial-qore.github.io/pyJMT/).

# Example
The following example shows the solution of a basic M/M/1 queueing system:
```
import pyJMT as jmt

def example_mm1():
    model = jmt.Network("M/M/1 model")
    source = jmt.Source(model, "mySource")
    queue = jmt.Queue(model, "myQueue", jmt.SchedStrategy.FCFS)
    sink = jmt.Sink(model, "mySink")

    openclass = jmt.OpenClass(model, "Class1")
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
```

You can alternatively run the above code as
```
pip install -r requirements.txt
python3 getting_started.py
```

Additional sample models are available in [examples.py](https://raw.githubusercontent.com/imperial-qore/pyJMT/main/examples.py).

# License
pyJMT is released as open source under the [BSD-3 license](https://raw.githubusercontent.com/imperial-qore/pyJMT/main/LICENSE).
