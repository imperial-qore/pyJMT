from enum_tools import DocumentedEnum


class DropStrategy(DocumentedEnum):
    DROP = "drop"  # doc: Represents the "drop" strategy.
    WAITING_QUEUE = "waiting queue"  # doc: Represents the "waiting queue" strategy.
    BAS_BLOCKING = "BAS blocking"  # doc: Represents the "BAS blocking" strategy.

