from enum import Enum


class Metrics(Enum):
    """
        An enumeration class representing the different types of metrics.

        :cvar NUM_CUSTOMERS: Represents the "Number of Customers" metric.
        :vartype NUM_CUSTOMERS: str
        :cvar QUEUE_TIME: Represents the "Queue Time" metric.
        :vartype QUEUE_TIME: str
        :cvar RESPONSE_TIME: Represents the "Response Time" metric.
        :vartype RESPONSE_TIME: str
        :cvar RESIDENCE_TIME: Represents the "Residence Time" metric.
        :vartype RESIDENCE_TIME: str
        :cvar ARRIVAL_RATE: Represents the "Arrival Rate" metric.
        :vartype ARRIVAL_RATE: str
        :cvar THROUGHPUT: Represents the "Throughput" metric.
        :vartype THROUGHPUT: str
        :cvar UTILIZATION: Represents the "Utilization" metric.
        :vartype UTILIZATION: str
        :cvar EFFECTIVE_UTILIZATION: Represents the "Effective Utilization" metric.
        :vartype EFFECTIVE_UTILIZATION: str
        :cvar DROP_RATE: Represents the "Drop Rate" metric.
        :vartype DROP_RATE: str
        :cvar BALKING_RATE: Represents the "Balking Rate" metric.
        :vartype BALKING_RATE: str
        :cvar RENEGING_RATE: Represents the "Reneging Rate" metric.
        :vartype RENEGING_RATE: str
        :cvar RETRIAL_RATE: Represents the "Retrial Rate" metric.
        :vartype RETRIAL_RATE: str
        :cvar RETRIAL_ORBIT_SIZE: Represents the "Retrial Orbit Size" metric.
        :vartype RETRIAL_ORBIT_SIZE: str
        :cvar RETRIAL_ORBIT_RESIDENCE_TIME: Represents the "Retrial Orbit Residence Time" metric.
        :vartype RETRIAL_ORBIT_RESIDENCE_TIME: str
        :cvar POWER: Represents the "Power" metric.
        :vartype POWER: str
        :cvar RESPONSE_TIME_PER_SINK: Represents the "Response Time per Sink" metric.
        :vartype RESPONSE_TIME_PER_SINK: str
        :cvar THROUGHPUT_PER_SINK: Represents the "Throughput per Sink" metric.
        :vartype THROUGHPUT_PER_SINK: str
        :cvar FORK_JOIN_NUM_CUSTOMERS: Represents the "Fork Join Number of Customers" metric.
        :vartype FORK_JOIN_NUM_CUSTOMERS: str
        :cvar FORK_JOIN_RESPONSE_TIME: Represents the "Fork Join Response Time" metric.
        :vartype FORK_JOIN_RESPONSE_TIME: str
        """
    NUM_CUSTOMERS = "Number of Customers"
    QUEUE_TIME = "Queue Time"
    RESPONSE_TIME = "Response Time"
    RESIDENCE_TIME = "Residence Time"
    ARRIVAL_RATE = "Arrival Rate"
    THROUGHPUT = "Throughput"
    UTILIZATION = "Utilization"
    EFFECTIVE_UTILIZATION = "Effective Utilization"
    DROP_RATE = "Drop Rate"
    BALKING_RATE = "Balking Rate"
    RENEGING_RATE = "Reneging Rate"
    RETRIAL_RATE = "Retrial Rate"
    RETRIAL_ORBIT_SIZE = "Retrial Orbit Size"
    RETRIAL_ORBIT_RESIDENCE_TIME = "Retrial Orbit Residence Time"
    POWER = "Power"
    RESPONSE_TIME_PER_SINK = "Response Time per Sink"
    THROUGHPUT_PER_SINK = "Throughput per Sink"
    FORK_JOIN_NUM_CUSTOMERS = "Fork Join Number of Customers"
    FORK_JOIN_RESPONSE_TIME = "Fork Join Response Time"
