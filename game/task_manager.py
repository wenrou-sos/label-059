import uuid
import time
from enum import Enum
from game.config import TASK_STATUSES, TASK_PRIORITIES


class TaskStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    @classmethod
    def from_string(cls, status_str):
        for status in cls:
            if status.value == status_str:
                return status
        raise ValueError(f"Invalid task status: {status_str}")


class TaskPriority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

    @classmethod
    def from_string(cls, priority_str):
        for priority in cls:
            if priority.value == priority_str:
                return priority
        raise ValueError(f"Invalid task priority: {priority_str}")


class Task:
    def __init__(self, title, description='', station_type=None,
                 priority='medium', target_count=10, due_time=None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.station_type = station_type
        self.priority = TaskPriority.from_string(priority)
        self.status = TaskStatus.PENDING
        self.target_count = target_count
        self.current_count = 0
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.started_at = None
        self.completed_at = None
        self.due_time = due_time

    def update(self, **kwargs):
        allowed_fields = ['title', 'description', 'station_type',
                          'priority', 'target_count', 'due_time']
        for key, value in kwargs.items():
            if key in allowed_fields:
                if key == 'priority' and isinstance(value, str):
                    value = TaskPriority.from_string(value)
                setattr(self, key, value)
        self.updated_at = time.time()

    def start(self):
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.IN_PROGRESS
            self.started_at = time.time()
            self.updated_at = self.started_at
            return True
        return False

    def complete(self):
        if self.status == TaskStatus.IN_PROGRESS:
            self.status = TaskStatus.COMPLETED
            self.completed_at = time.time()
            self.updated_at = self.completed_at
            return True
        return False

    def cancel(self):
        if self.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            self.status = TaskStatus.CANCELLED
            self.updated_at = time.time()
            return True
        return False

    def reset(self):
        self.status = TaskStatus.PENDING
        self.current_count = 0
        self.started_at = None
        self.completed_at = None
        self.updated_at = time.time()

    def increment_progress(self, amount=1):
        if self.status == TaskStatus.IN_PROGRESS:
            self.current_count += amount
            self.updated_at = time.time()
            if self.current_count >= self.target_count:
                self.complete()
            return True
        return False

    def get_progress_percentage(self):
        if self.target_count == 0:
            return 100.0
        return min(100.0, (self.current_count / self.target_count) * 100)

    def is_overdue(self):
        if self.due_time is None:
            return False
        return time.time() > self.due_time and self.status != TaskStatus.COMPLETED

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'station_type': self.station_type,
            'priority': self.priority.value,
            'status': self.status.value,
            'target_count': self.target_count,
            'current_count': self.current_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'due_time': self.due_time
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            station_type=data.get('station_type'),
            priority=data.get('priority', 'medium'),
            target_count=data.get('target_count', 10),
            due_time=data.get('due_time')
        )
        task.id = data['id']
        task.status = TaskStatus.from_string(data['status'])
        task.current_count = data.get('current_count', 0)
        task.created_at = data.get('created_at', time.time())
        task.updated_at = data.get('updated_at', task.created_at)
        task.started_at = data.get('started_at')
        task.completed_at = data.get('completed_at')
        return task

    def __repr__(self):
        return f"<Task id={self.id} title='{self.title}' status={self.status.value}>"


class TaskManager:
    def __init__(self):
        self.tasks = {}
        self._next_order = []

    def create_task(self, title, description='', station_type=None,
                    priority='medium', target_count=10, due_time=None):
        task = Task(
            title=title,
            description=description,
            station_type=station_type,
            priority=priority,
            target_count=target_count,
            due_time=due_time
        )
        self.tasks[task.id] = task
        self._next_order.append(task.id)
        return task

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def edit_task(self, task_id, **kwargs):
        task = self.get_task(task_id)
        if task:
            task.update(**kwargs)
            return task
        return None

    def delete_task(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]
            if task_id in self._next_order:
                self._next_order.remove(task_id)
            return True
        return False

    def start_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            return task.start()
        return False

    def complete_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            return task.complete()
        return False

    def cancel_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            return task.cancel()
        return False

    def reset_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            task.reset()
            return True
        return False

    def set_task_status(self, task_id, new_status):
        task = self.get_task(task_id)
        if not task:
            return False
        if isinstance(new_status, str):
            new_status = TaskStatus.from_string(new_status)

        if new_status == task.status:
            return True

        if new_status == TaskStatus.PENDING:
            task.reset()
        elif new_status == TaskStatus.IN_PROGRESS:
            if task.status == TaskStatus.PENDING:
                task.start()
            elif task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                task.status = TaskStatus.IN_PROGRESS
                if not task.started_at:
                    task.started_at = time.time()
                task.updated_at = time.time()
        elif new_status == TaskStatus.COMPLETED:
            if task.status == TaskStatus.IN_PROGRESS:
                task.complete()
            elif task.status == TaskStatus.PENDING:
                task.start()
                task.complete()
            elif task.status == TaskStatus.CANCELLED:
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = time.time()
                task.complete()
        elif new_status == TaskStatus.CANCELLED:
            task.cancel()
        return True

    def update_progress(self, station_type=None, amount=1):
        updated = []
        for task in self.tasks.values():
            if task.status == TaskStatus.IN_PROGRESS:
                if station_type is None or task.station_type is None or task.station_type == station_type:
                    task.increment_progress(amount)
                    if task.status == TaskStatus.COMPLETED:
                        updated.append(task)
        return updated

    def list_tasks(self, status_filter=None, priority_filter=None,
                   station_filter=None, sort_by='created_at', reverse=True):
        tasks = list(self.tasks.values())

        if status_filter:
            if isinstance(status_filter, str):
                status_filter = [status_filter]
            status_set = set(status_filter)
            tasks = [t for t in tasks if t.status.value in status_set]

        if priority_filter:
            if isinstance(priority_filter, str):
                priority_filter = [priority_filter]
            priority_set = set(priority_filter)
            tasks = [t for t in tasks if t.priority.value in priority_set]

        if station_filter:
            if isinstance(station_filter, str):
                station_filter = [station_filter]
            station_set = set(station_filter)
            tasks = [t for t in tasks if t.station_type in station_set]

        sort_key = getattr(self, f'_sort_by_{sort_by}', None)
        if sort_key:
            tasks.sort(key=sort_key, reverse=reverse)
        else:
            tasks.sort(key=lambda t: t.created_at, reverse=reverse)

        return tasks

    def _sort_by_created_at(self, task):
        return task.created_at

    def _sort_by_updated_at(self, task):
        return task.updated_at

    def _sort_by_priority(self, task):
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        return priority_order[task.priority.value]

    def _sort_by_status(self, task):
        status_order = {'in_progress': 0, 'pending': 1, 'completed': 2, 'cancelled': 3}
        return status_order[task.status.value]

    def _sort_by_progress(self, task):
        return task.get_progress_percentage()

    def get_task_count(self, status_filter=None):
        if status_filter:
            return len(self.list_tasks(status_filter=status_filter))
        return len(self.tasks)

    def get_active_task_for_station(self, station_type):
        for task in self.tasks.values():
            if (task.status == TaskStatus.IN_PROGRESS and
                    task.station_type == station_type):
                return task
        return None

    def clear_completed(self):
        to_remove = [tid for tid, t in self.tasks.items()
                     if t.status == TaskStatus.COMPLETED]
        for tid in to_remove:
            self.delete_task(tid)
        return len(to_remove)

    def clear_all(self):
        count = len(self.tasks)
        self.tasks.clear()
        self._next_order.clear()
        return count

    def to_dict(self):
        return {
            'tasks': [t.to_dict() for t in self.tasks.values()]
        }

    @classmethod
    def from_dict(cls, data):
        manager = cls()
        for task_data in data.get('tasks', []):
            task = Task.from_dict(task_data)
            manager.tasks[task.id] = task
            manager._next_order.append(task.id)
        return manager
