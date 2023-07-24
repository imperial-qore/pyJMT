class JobClass:
    def __init__(self, model, name, priority):
        self.model = model
        self.name = name
        self.priority = priority

class OpenClass(JobClass):
    """
        This is the OpenClass, it's intended to represent an open job class.

        :param model: The model to which this class belongs.
        :type model: Network
        :param name: The name of the class.
        :type name: str
        :param priority: The priority of this class, default is 0.
        :type priority: int
        """
    def __init__(self, model, name, priority=0):
        JobClass.__init__(self, model, name, priority)
        self.model.classes.append(self)
        self.referenceSource = None


class ClosedClass(JobClass):
    """
       This is the ClosedClass, it's intended to represent a closed job class.

       :param model: The model to which this class belongs.
       :type model: Network
       :param name: The name of the class.
       :type name: str
       :param population: The population of this class.
       :type population: int
       :param sourceNode: The source node for this class.
       :type sourceNode: Node
       :param priority: The priority of this class, default is 0.
       :type priority: int
       """
    def __init__(self, model, name, population, sourceNode, priority=0):
        JobClass.__init__(self, model, name, priority)
        self.model.classes.append(self)
        self.referenceSource = sourceNode.name
        self.sourceNode = sourceNode
        self.population = population

