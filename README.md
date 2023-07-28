# pyJMT
The pyJMT package is a Python wrapper for the Java Modelling Tools (JMT) suite, which is used for performance evaluation of systems using queueing network models.
Using this tool one can model and simulate different networks in python.

A short getting started guide along with installation instructions can be found on [GitHub](https://github.com/imperial-qore/pyJMT/blob/main/pyJMT_docs.pdf), with full documentation available [here](https://imperial-qore.github.io/pyJMT/).

# Working on pyJMT:
The project can be found on [GitHub](https://github.com/imperial-qore/pyJMT)\
To build the documentation locally, in the docs directory run `make html` then open index.html\
The documentation will automatically be built and uploaded to the github pages website on push.\
To push changes to the package on PyPi, change the version number in conf.py and setup.py, then run the following commands.
```
python setup.py sdist bdist_wheel
twine upload dist/*
```
