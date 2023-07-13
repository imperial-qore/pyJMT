from enum import Enum
import os


class SchedStrategy(Enum):
    FCFS = "FCFS"
    PS = "PS"
    # Add other scheduling strategies here as needed


class RoutingStrategy(Enum):
    RROBIN = "RROBIN"
    RANDOM = "RANDOM"
    PROBABILITIES = "PROBABILITIES"
    # Add other routing strategies here as needed


class Exp:
    def __init__(self, lambda_value):
        self.lambda_value = lambda_value


class Erlang:
    def __init__(self, alpha, r):
        self.alpha = alpha
        self.r = r

    @staticmethod
    def fitMeanAndSCV(mean, scv):
        r = 1/scv
        alpha = r/mean
        return Erlang(alpha, r)

    @staticmethod
    def fitMeanAndOrder(mean, order):
        r = order
        alpha = order / mean
        return Erlang(alpha, r)

class Replayer:
    def __init__(self, fileName):
        self.fileName = os.getcwd() + "/" + fileName