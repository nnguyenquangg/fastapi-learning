import json
import os

def load_tasks(filename= "todos.json"):
    if not os.path.exists(filename):
        return[]
    with open(filename, 'r', encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else []
    
def save_tasks(tasks, filename= "todos.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def get_next_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1