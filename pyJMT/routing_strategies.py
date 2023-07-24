from enum import Enum

# Each enum element's value is laid out like so:
#
#         - RoutingStrategy.element.value[0] is the name of the type of Routing strategy.
#         - RoutingStrategy.element.value[1] is the name of routing strategy.
#         - RoutingStrategy.element.value[2] is the name of strategy under RoutingStrategies in xml.

class RoutingStrategy(Enum):
    """
        Enum for all Routing strategies.

        :cvar RANDOM: Random routing strategy.
        :vartype RANDOM: list
        :cvar RROBIN: Round Robin routing strategy.
        :vartype RROBIN: list
        :cvar JSQ: Join the Shortest Queue (JSQ) routing strategy.
        :vartype JSQ: list
        :cvar SHORTEST_RESPONSE_TIME: Shortest Response Time routing strategy.
        :vartype SHORTEST_RESPONSE_TIME: list
        :cvar LEAST_UTILIZATION: Least Utilization routing strategy.
        :vartype LEAST_UTILIZATION: list
        :cvar FASTEST_SERVICE: Fastest Service routing strategy.
        :vartype FASTEST_SERVICE: list
        :cvar DISABLED: Disabled routing strategy.
        :vartype DISABLED: list
        :cvar PROB: Probabilities routing strategy.
        :vartype PROB: list
        :cvar CLASSSWITCH: Class Switch routing strategy.
        :vartype CLASSSWITCH: list
        """

    RANDOM = ["Static", "Random", "RandomStrategy"]
    RROBIN = ["Static", "Round Robin", "RoundRobinStrategy"]
    JSQ = ["Static", "Join the Shortest Queue (JSQ)", "ShortestQueueLengthRoutingStrategy"]
    SHORTEST_RESPONSE_TIME = ["Static", "Shortest Response Time", "ShortestResponseTimeRoutingStrategy"]
    LEAST_UTILIZATION = ["Static", "Least Utilization", "LeastUtilizationRoutingStrategy"]
    FASTEST_SERVICE = ["Static", "Fastest Service", "FastestServiceRoutingStrategy"]
    DISABLED = ["Static", "Disabled", "DisabledRoutingStrategy"]
    PROB = ["Prob", "Probabilities", "RandomStrategy"]
    CLASSSWITCH = ["ClassSwitch", "Class Switch", "ClassSwitchRoutingStrategy" ]
