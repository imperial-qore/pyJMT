from enum import Enum

class RoutingStrategy(Enum):
    RROBIN = "RROBIN"
    RANDOM = "RANDOM"
    PROBABILITIES = "PROBABILITIES"
    # Add other routing strategies here as needed