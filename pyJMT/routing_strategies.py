from enum_tools import DocumentedEnum

# Each enum element's value is laid out like so:
#
#         - RoutingStrategy.element.value[0] is the name of the type of Routing strategy.
#         - RoutingStrategy.element.value[1] is the name of routing strategy.
#         - RoutingStrategy.element.value[2] is the name of strategy under RoutingStrategies in xml.


class RoutingStrategy(DocumentedEnum):
    RANDOM = ["Static", "Random", "RandomStrategy"]  # doc: Random routing strategy.
    RROBIN = ["Static", "Round Robin", "RoundRobinStrategy"]  # doc: Round Robin routing strategy.
    JSQ = ["Static", "Join the Shortest Queue (JSQ)", "ShortestQueueLengthRoutingStrategy"]  # doc: Join the Shortest Queue (JSQ) routing strategy.
    SHORTEST_RESPONSE_TIME = ["Static", "Shortest Response Time", "ShortestResponseTimeRoutingStrategy"]  # doc: Shortest Response Time routing strategy.
    LEAST_UTILIZATION = ["Static", "Least Utilization", "LeastUtilizationRoutingStrategy"]  # doc: Least Utilization routing strategy.
    FASTEST_SERVICE = ["Static", "Fastest Service", "FastestServiceRoutingStrategy"]  # doc: Fastest Service routing strategy.
    DISABLED = ["Static", "Disabled", "DisabledRoutingStrategy"]  # doc: Disabled routing strategy.
    PROB = ["Prob", "Probabilities", "RandomStrategy"]  # doc: Probabilities routing strategy.
    CLASSSWITCH = ["ClassSwitch", "Class Switch", "ClassSwitchRoutingStrategy"]  # doc: Class Switch routing strategy.

