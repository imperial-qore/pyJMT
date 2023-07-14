from enum import Enum


class SchedStrategy(Enum):
    """Enum for all queue scheduling strategies
        Each enum element's value is laid out like so:
        SchedStrategy.element.value[0] is the name of the type of scheduling strategy
        SchedStrategy.element.value[1] is the name of strategy under QueuePutStrategies
        SchedStrategy.element.value[2] is the type of strategy under PSStrategies - only PS strategies get this value"""

    # Non preemptive scheduling strategies
    FCFS = ["NP", "TailStrategy"]
    """Non-preemptive FCFS policy"""

    LCFS = ["NP", "HeadStrategy"]
    """Non-preemptive LCFS policy"""

    RAND = ["NP", "RandStrategy"]
    """Non-preemptive RAND policy"""

    SJF = ["NP", "SJFStrategy"]
    """Non-preemptive SJF policy"""

    LJF = ["NP", "LJFStrategy"]
    """Non-preemptive LJF policy"""

    SEPT = ["NP", "SEPTStrategy"]
    """Non-preemptive SEPT policy"""

    LEPT = ["NP", "LEPTStrategy"]
    """Non-preemptive LEPT policy"""

    # Preemptive scheduling strategies
    FCFS_PR = ["P", "FCFSPRStrategy"]
    """Preemptive FCFS policy"""

    LCFS_PR = ["P", "LCFSPRStrategy"]
    """Preemptive LCFS policy"""

    SRPT = ["P", "SRPTStrategy"]
    """Preemptive SRPT policy"""

    # Processor Sharing scheduling strategies
    PS = ["PS", "TailStrategy", "EPSStrategy"]
    """Processor Sharing PS policy"""

    DPS = ["PS", "TailStrategy", "DPSStrategy"]
    """Processor Sharing DPS policy"""

    GPS = ["PS", "TailStrategy", "GPSStrategy"]
    """Processor Sharing GPS policy"""

    # Add other scheduling strategies here as needed
