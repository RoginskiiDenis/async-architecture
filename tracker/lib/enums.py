import enum


class Role(enum.Enum):
    WORKER = 'worker'
    ADMIN = 'admin'
    ACCOUNTANT = 'accountant'
    MANAGER = 'manager'
