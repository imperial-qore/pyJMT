from enum import Enum


class DropStrategy(Enum):
    """
    An enumeration class representing the different strategies to handle dropping.

    :cvar DROP: Represents the "drop" strategy.
    :vartype DROP: str
    :cvar WAITING_QUEUE: Represents the "waiting queue" strategy.
    :vartype WAITING_QUEUE: str
    :cvar BAS_BLOCKING: Represents the "BAS blocking" strategy.
    :vartype BAS_BLOCKING: str
    """
    DROP = "drop"
    WAITING_QUEUE = "waiting queue"
    BAS_BLOCKING = "BAS blocking"
