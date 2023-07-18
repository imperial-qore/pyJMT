class OpenClass:
    def __init__(self, model, name, priority=0):
        self.model = model
        self.name = name
        self.model.classes.append(self)
        self.referenceSource = None
        self.priority = priority


class ClosedClass:
    def __init__(self, model, name, population, sourceNode, priority=0):
        self.model = model
        self.name = name
        self.model.classes.append(self)
        self.referenceSource = sourceNode.name
        self.sourceNode = sourceNode
        self.population = population
        self.priority = priority

