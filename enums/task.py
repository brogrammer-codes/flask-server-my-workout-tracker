from enum import Enum

class TaskTypes(Enum):
    FOLDER = 'folder'
    ROUTINE= 'routine'
    PLAN= 'plan'
    ACTIVITY= 'activity'
    SUPERSET= 'superset'
    HEADER= 'header'
    