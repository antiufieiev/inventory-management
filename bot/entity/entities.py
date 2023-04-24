from enum import IntEnum


class AccessLevel(IntEnum):
    ADMIN = 10000,
    MANAGER = 10,
    EMPLOYEE = 1,
    NONE = 0
