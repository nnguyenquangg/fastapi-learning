import sys
import argparse
from storage import load_tasks, save_tasks, get_next_id
from models import new_task, TaskNotFoundError

def cmd_add(title, priority="normal", due=None):
    tasks = load_tasks()
    tasks.append(new_task(get_next_id(tasks), title, priority, due))
    save_tasks(tasks)
    print(f"Added: {title} ({priority})")

def cmd_list(status=None, sort_due=False):
    tasks = load_tasks()
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if sort_due:
        tasks = sorted(tasks, key=lambda t: (t.get("due") is None, t.get("due")))
    for t in tasks:
        due_str = f" (due {t['due']})" if t.get("due") else ""
        print(f"[{t['id']}] {t['title']} ({t['priority']}){due_str}")

def find_task(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise TaskNotFoundError(f"Không tìm thấy task với id={task_id}")

def cmd_done(task_id):
    tasks = load_tasks()
    try:
        task = find_task(tasks, task_id)
    except TaskNotFoundError as e:
        print(f"Lỗi: {e}")
        return
    task["status"] = "done"
    save_tasks(tasks)
    print(f"Marked done: {task['title']}")

def cmd_delete(task_id):
    tasks = load_tasks()
    try:
        task = find_task(tasks, task_id)
    except TaskNotFoundError as e:
        print(f"Lỗi: {e}")
        return
    tasks.remove(task)
    save_tasks(tasks)
    print(f"Deleted: {task['title']}")

def cmd_clear(done=False):
    tasks = load_tasks()
    if done:
        remaining = [t for t in tasks if t["status"] != "done"]
        print(f"Cleared {len(tasks) - len(remaining)} done items")
        save_tasks(remaining)

def cmd_search(keyword):
    tasks = load_tasks()
    keyword = keyword.lower()
    results = [t for t in tasks if keyword in t["title"].lower()]
    if not results:
        print(f"Không tìm thấy task nào chứa: {keyword}")
        return
    for t in results:
        print(f"[{t['id']}] {t['title']} ({t['priority']})")

def cmd_export():
    tasks = load_tasks()
    lines = ["# Todo List", ""]
    for t in tasks:
        box = "x" if t["status"] == "done" else " "
        lines.append(f"- [{box}] {t['title']} ({t['priority']})")
    print("\n".join(lines))

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command", required=True)

p_add = subparsers.add_parser("add")
p_add.add_argument("title")
p_add.add_argument("--priority", choices=["low", "normal", "high"], default="normal")
p_add.add_argument("--due", default=None)

p_done = subparsers.add_parser("done")
p_done.add_argument("id", type=int)

p_delete = subparsers.add_parser("delete")
p_delete.add_argument("id", type=int)

p_list = subparsers.add_parser("list")
p_list.add_argument("--status", choices=["pending", "done"], default=None)
p_list.add_argument("--due", action="store_true")

p_search = subparsers.add_parser("search")
p_search.add_argument("keyword")

p_export = subparsers.add_parser("export")

p_clear = subparsers.add_parser("clear")
p_clear.add_argument("--done", action="store_true")

args = parser.parse_args()

if args.command == "add":
    cmd_add(args.title, args.priority, args.due)
elif args.command == "list":
    cmd_list(args.status, args.due)

elif args.command == "done":
    cmd_done(args.id)
elif args.command == "delete":
    cmd_delete(args.id)

elif args.command == "search":
    cmd_search(args.keyword)

elif args.command == "export":
    cmd_export()

elif args.command == "clear":
    cmd_clear(args.done)