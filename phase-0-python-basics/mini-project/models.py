from datetime import datetime

PRIORITIES = ('low', 'normal', 'high')
STATUSES = ('pending', 'done')

def new_task(id, title, priority="normal", due=None):
    return{
        "id": id,
        "title": title,
        "priority": priority,
        "status": "pending",
        "due": due
    }

class TaskNotFoundError(Exception):
    """Raise khi không tìm thấy task với id được yêu cầu."""
    pass
