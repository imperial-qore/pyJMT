from enum_tools import DocumentedEnum


# Each enum element's value is laid out like so:

# - SchedStrategy.element.value[0] is the name of the type of scheduling strategy
# - SchedStrategy.element.value[1] is the name of strategy under QueuePutStrategies
# - SchedStrategy.element.value[2] is the type of strategy under PSStrategies - only PS strategies get this value
class SchedStrategy(DocumentedEnum):
    FCFS = ["NP", "TailStrategy"]  # doc: Non-preemptive FCFS policy
    FCFS_PRIORITY = ["NP", "TailStrategyPriority"]  # doc: Non-preemptive priority based FCFS policy
    LCFS = ["NP", "HeadStrategy"]  # doc: Non-preemptive LCFS policy
    LCFS_PRIORITY = ["NP", "HeadStrategyPriority"]  # doc: Non-preemptive priority based LCFS policy
    RAND = ["NP", "RandStrategy"]  # doc: Non-preemptive RAND policy
    RAND_PRIORITY = ["NP", "RandStrategyPriority"]  # doc: Non-preemptive priority based RAND policy
    SJF = ["NP", "SJFStrategy"]  # doc: Non-preemptive SJF policy
    SJF_PRIORITY = ["NP", "SJFStrategyPriority"]  # doc: Non-preemptive priority based SJF policy
    LJF = ["NP", "LJFStrategy"]  # doc: Non-preemptive LJF policy
    LJF_PRIORITY = ["NP", "LJFStrategyPriority"]  # doc: Non-preemptive priority based LJF policy
    SEPT = ["NP", "SEPTStrategy"]  # doc: Non-preemptive SEPT policy
    SEPT_PRIORITY = ["NP", "SEPTStrategyPriority"]  # doc: Non-preemptive priority based SEPT policy
    LEPT = ["NP", "LEPTStrategy"]  # doc: Non-preemptive LEPT policy
    LEPT_PRIORITY = ["NP", "LEPTStrategyPriority"]  # doc: Non-preemptive priority based LEPT policy
    FCFS_PR = ["P", "FCFSPRStrategy"]  # doc: Preemptive FCFS policy
    FCFS_PR_PRIORITY = ["P", "FCFSPRStrategyPriority"]  # doc: Preemptive priority based FCFS policy
    LCFS_PR = ["P", "LCFSPRStrategy"]  # doc: Preemptive LCFS policy
    LCFS_PR_PRIORITY = ["P", "LCFSPRStrategyPriority"]  # doc: Preemptive priority based LCFS policy
    SRPT = ["P", "SRPTStrategy"]  # doc: Preemptive SRPT policy
    SRPT_PRIORITY = ["P", "SRPTStrategyPriority"]  # doc: Preemptive priority based SRPT policy
    PS = ["PS", "TailStrategy", "EPSStrategy"]  # doc: Processor Sharing PS policy
    DPS = ["PS", "TailStrategy", "DPSStrategy"]  # doc: Processor Sharing DPS policy
    GPS = ["PS", "TailStrategy", "GPSStrategy"]  # doc: Processor Sharing GPS policy

