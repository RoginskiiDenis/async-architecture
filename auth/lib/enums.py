import enum

class Role(enum.Enum):
    WORKER = 'worker'
    ADMIN = 'admin'
    ACCOUNTANT = 'accountant'
    MANAGER = 'manager'

ROLE_VALUES = set([item.value for item in Role])
