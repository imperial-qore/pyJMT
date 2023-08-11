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

This example will print out:
```
Station  JobClass analyzedSamples meanValue           successful discardedSamples measureType         lowerLimit          nodeType alfa precision upperLimit         maxSamples 
myQueue  Class1 450560          0.9891299381139143  true       760              Number of Customers 0.9661755892808247  station  0.01 0.03      1.012084286947004  1000000    
myQueue  Class1 46080           0.496953737041098   true       630              Utilization         0.48488393655927425 station  0.01 0.03      0.5090235375229217 1000000    
myQueue  Class1 163840          1.97685030594545    true       190              Response Time       1.9305222048085555  station  0.01 0.03      2.0231784070823444 1000000    
myQueue  Class1 61440           0.49916726343571804 true       115              Throughput          0.4894933226429664  station  0.01 0.03      0.5092312890562263 1000000    
myQueue  Class1 61440           0.4991462764898616  true       115              Arrival Rate        0.48942754624081064 station  0.01 0.03      0.5092588027856187 1000000    
mySource Class1 61440           0.4991462764898616  true       115              Throughput          0.48942754624081064 station  0.01 0.03      0.5092588027856187 1000000    
mySource Class1 61440           0.4991462764898616  true       115              Arrival Rate        0.48942754624081064 station  0.01 0.03      0.5092588027856187 1000000    
```
and the simulation result file will be made  available under the output_files/ folder.  Additional usage examples are available in [examples.py](https://raw.githubusercontent.com/imperial-qore/pyJMT/main/examples.py).

# License
pyJMT is released as open source under the [BSD-3 license](https://raw.githubusercontent.com/imperial-qore/pyJMT/main/LICENSE).
