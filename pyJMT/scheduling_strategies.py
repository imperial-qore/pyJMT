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

    FCFS_PRIORITY = ["NP", "TailStrategyPriority"]
    """Non-preemptive priority based FCFS policy"""

    LCFS = ["NP", "HeadStrategy"]
    """Non-preemptive LCFS policy"""

    LCFS_PRIORITY = ["NP", "HeadStrategyPriority"]
    """Non-preemptive priority based LCFS policy"""

    RAND = ["NP", "RandStrategy"]
    """Non-preemptive RAND policy"""

    RAND_PRIORITY = ["NP", "RandStrategyPriority"]
    """Non-preemptive priority based RAND policy"""

    SJF = ["NP", "SJFStrategy"]
    """Non-preemptive SJF policy"""

    SJF_PRIORITY = ["NP", "SJFStrategyPriority"]
    """Non-preemptive priority based SJF policy"""

    LJF = ["NP", "LJFStrategy"]
    """Non-preemptive LJF policy"""

    LJF_PRIORITY = ["NP", "LJFStrategyPriority"]
    """Non-preemptive priority based LJF policy"""

    SEPT = ["NP", "SEPTStrategy"]
    """Non-preemptive SEPT policy"""

    SEPT_PRIORITY = ["NP", "SEPTStrategyPriority"]
    """Non-preemptive priority based SEPT policy"""

    LEPT = ["NP", "LEPTStrategy"]
    """Non-preemptive LEPT policy"""

    LEPT_PRIORITY = ["NP", "LEPTStrategyPriority"]
    """Non-preemptive priority based LEPT policy"""

    # Preemptive scheduling strategies
    FCFS_PR = ["P", "FCFSPRStrategy"]
    """Preemptive FCFS policy"""

    FCFS_PR_PRIORITY = ["P", "FCFSPRStrategyPriority"]
    """Preemptive priority based FCFS policy"""

    LCFS_PR = ["P", "LCFSPRStrategy"]
    """Preemptive LCFS policy"""

    LCFS_PR_PRIORITY = ["P", "LCFSPRStrategyPriority"]
    """Preemptive priority based LCFS policy"""

    SRPT = ["P", "SRPTStrategy"]
    """Preemptive SRPT policy"""

    SRPT_PRIORITY = ["P", "SRPTStrategyPriority"]
    """Preemptive priority based SRPT policy"""

    # Processor Sharing scheduling strategies
    PS = ["PS", "TailStrategy", "EPSStrategy"]
    """Processor Sharing PS policy"""

    DPS = ["PS", "TailStrategy", "DPSStrategy"]
    """Processor Sharing DPS policy"""

    GPS = ["PS", "TailStrategy", "GPSStrategy"]
    """Processor Sharing GPS policy"""

    # Add other scheduling strategies here as needed
