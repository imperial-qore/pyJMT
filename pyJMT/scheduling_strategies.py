from enum import Enum


# Each enum element's value is laid out like so:

# - SchedStrategy.element.value[0] is the name of the type of scheduling strategy
# - SchedStrategy.element.value[1] is the name of strategy under QueuePutStrategies
# - SchedStrategy.element.value[2] is the type of strategy under PSStrategies - only PS strategies get this value
class SchedStrategy(Enum):
    """Enum for all queue scheduling strategies
    Strategies
    ----------

    .. py:attribute:: FCFS

        Non-preemptive FCFS policy

    .. py:attribute:: FCFS_PRIORITY

        Non-preemptive priority based FCFS policy

    .. py:attribute:: LCFS

        Non-preemptive LCFS policy

    .. py:attribute:: LCFS_PRIORITY

        Non-preemptive priority based LCFS policy

    .. py:attribute:: RAND

        Non-preemptive RAND policy

    .. py:attribute:: RAND_PRIORITY

        Non-preemptive priority based RAND policy

    .. py:attribute:: SJF

        Non-preemptive SJF policy

    .. py:attribute:: SJF_PRIORITY

        Non-preemptive priority based SJF policy

    .. py:attribute:: LJF

        Non-preemptive LJF policy

    .. py:attribute:: LJF_PRIORITY

        Non-preemptive priority based LJF policy

    .. py:attribute:: SEPT

        Non-preemptive SEPT policy

    .. py:attribute:: SEPT_PRIORITY

        Non-preemptive priority based SEPT policy

    .. py:attribute:: LEPT

        Non-preemptive LEPT policy

    .. py:attribute:: LEPT_PRIORITY

        Non-preemptive priority based LEPT policy

    .. py:attribute:: FCFS_PR

        Preemptive FCFS policy

    .. py:attribute:: FCFS_PR_PRIORITY

        Preemptive priority based FCFS policy

    .. py:attribute:: LCFS_PR

        Preemptive LCFS policy

    .. py:attribute:: LCFS_PR_PRIORITY

        Preemptive priority based LCFS policy

    .. py:attribute:: SRPT

        Preemptive SRPT policy

    .. py:attribute:: SRPT_PRIORITY

        Preemptive priority based SRPT policy

    .. py:attribute:: PS

        Processor Sharing PS policy

    .. py:attribute:: DPS

        Processor Sharing DPS policy

    .. py:attribute:: GPS

        Processor Sharing GPS policy

    """

    # Non preemptive scheduling strategies
    FCFS = ["NP", "TailStrategy"]

    FCFS_PRIORITY = ["NP", "TailStrategyPriority"]

    LCFS = ["NP", "HeadStrategy"]

    LCFS_PRIORITY = ["NP", "HeadStrategyPriority"]

    RAND = ["NP", "RandStrategy"]

    RAND_PRIORITY = ["NP", "RandStrategyPriority"]

    SJF = ["NP", "SJFStrategy"]

    SJF_PRIORITY = ["NP", "SJFStrategyPriority"]

    LJF = ["NP", "LJFStrategy"]

    LJF_PRIORITY = ["NP", "LJFStrategyPriority"]

    SEPT = ["NP", "SEPTStrategy"]

    SEPT_PRIORITY = ["NP", "SEPTStrategyPriority"]

    LEPT = ["NP", "LEPTStrategy"]

    LEPT_PRIORITY = ["NP", "LEPTStrategyPriority"]

    # Preemptive scheduling strategies
    FCFS_PR = ["P", "FCFSPRStrategy"]

    FCFS_PR_PRIORITY = ["P", "FCFSPRStrategyPriority"]

    LCFS_PR = ["P", "LCFSPRStrategy"]

    LCFS_PR_PRIORITY = ["P", "LCFSPRStrategyPriority"]

    SRPT = ["P", "SRPTStrategy"]

    SRPT_PRIORITY = ["P", "SRPTStrategyPriority"]

    # Processor Sharing scheduling strategies
    PS = ["PS", "TailStrategy", "EPSStrategy"]

    DPS = ["PS", "TailStrategy", "DPSStrategy"]

    GPS = ["PS", "TailStrategy", "GPSStrategy"]

    # Add other scheduling strategies here as needed
