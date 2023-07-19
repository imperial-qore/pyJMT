from enum import Enum

class DropStrategy(Enum):
    DROP = "drop"
    WAITING_QUEUE = "waiting queue"
    BAS_BLOCKING = "BAS blocking"
