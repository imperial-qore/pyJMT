from enum import Enum

class RoutingStrategy(Enum):
    """Enum for all Routing strategies
    Each enum element's value is laid out like so:
    RoutingStrategy.element.value[0] is the name of the type of Routing strategy
    RoutingStrategy.element.value[1] is the name of routing strategy
    RoutingStrategy.element.value[0] is the name of strategy under RoutingStrategies in xml """

    RANDOM = ["Static", "Random", "RandomStrategy"]
    RROBIN = ["Static", "Round Robin", "RoundRobinStrategy"]
    JSQ = ["Static", "Join the Shortest Queue (JSQ)", "ShortestQueueLengthRoutingStrategy"]
    SHORTEST_RESPONSE_TIME = ["Static", "Shortest Response Time", "ShortestResponseTimeRoutingStrategy"]
    LEAST_UTILIZATION = ["Static", "Least Utilization", "LeastUtilizationRoutingStrategy"]
    FASTEST_SERVICE = ["Static", "Fastest Service", "FastestServiceRoutingStrategy"]
    DISABLED = ["Static", "Disabled", "DisabledRoutingStrategy"]
    PROB = ["Prob", "Probabilities", "RandomStrategy"]
    CLASSSWITCH = ["ClassSwitch", "Class Switch", "ClassSwitchRoutingStrategy" ]
