from enum import Enum


class Metrics(Enum):
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
