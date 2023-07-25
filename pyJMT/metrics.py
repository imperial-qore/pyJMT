from enum_tools import DocumentedEnum

class Metrics(DocumentedEnum):
    NUM_CUSTOMERS = "Number of Customers"  # doc: Represents the "Number of Customers" metric.
    QUEUE_TIME = "Queue Time"  # doc: Represents the "Queue Time" metric.
    RESPONSE_TIME = "Response Time"  # doc: Represents the "Response Time" metric.
    RESIDENCE_TIME = "Residence Time"  # doc: Represents the "Residence Time" metric.
    ARRIVAL_RATE = "Arrival Rate"  # doc: Represents the "Arrival Rate" metric.
    THROUGHPUT = "Throughput"  # doc: Represents the "Throughput" metric.
    UTILIZATION = "Utilization"  # doc: Represents the "Utilization" metric.
    EFFECTIVE_UTILIZATION = "Effective Utilization"  # doc: Represents the "Effective Utilization" metric.
    DROP_RATE = "Drop Rate"  # doc: Represents the "Drop Rate" metric.
    BALKING_RATE = "Balking Rate"  # doc: Represents the "Balking Rate" metric.
    RENEGING_RATE = "Reneging Rate"  # doc: Represents the "Reneging Rate" metric.
    RETRIAL_RATE = "Retrial Rate"  # doc: Represents the "Retrial Rate" metric.
    RETRIAL_ORBIT_SIZE = "Retrial Orbit Size"  # doc: Represents the "Retrial Orbit Size" metric.
    RETRIAL_ORBIT_RESIDENCE_TIME = "Retrial Orbit Residence Time"  # doc: Represents the "Retrial Orbit Residence Time" metric.
    POWER = "Power"  # doc: Represents the "Power" metric.
    RESPONSE_TIME_PER_SINK = "Response Time per Sink"  # doc: Represents the "Response Time per Sink" metric.
    THROUGHPUT_PER_SINK = "Throughput per Sink"  # doc: Represents the "Throughput per Sink" metric.
    FORK_JOIN_NUM_CUSTOMERS = "Fork Join Number of Customers"  # doc: Represents the "Fork Join Number of Customers" metric.
    FORK_JOIN_RESPONSE_TIME = "Fork Join Response Time"  # doc: Represents the "Fork Join Response Time" metric.
