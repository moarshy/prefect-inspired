import asyncio
import functools
import traceback
from datetime import datetime
from enum import Enum, auto
import uuid

from engine.db import save_task_result, save_workflow_result

class TaskState(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()

class TaskResult:
    def __init__(self, name, id=None):
        self.name = name
        self.id = id or str(uuid.uuid4())
        self.state = TaskState.PENDING
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.input_data = None
        self.output_data = None
        self.error_message = None
        self.retries = 0

    def start(self, input_data):
        self.state = TaskState.RUNNING
        self.start_time = datetime.now()
        self.input_data = input_data
        print(f"{self.name} state: {self.state}, Input: {self.input_data}")

    def complete(self, output_data):
        self.state = TaskState.SUCCESS
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        self.output_data = output_data
        print(f"{self.name} state: {self.state}, Duration: {self.duration}, Output: {self.output_data}")

    def fail(self, error_message):
        self.state = TaskState.FAILED
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        self.error_message = error_message
        print(f"{self.name} state: {self.state}, Error: {self.error_message}, Retries: {self.retries}")

    def increment_retries(self):
        self.retries += 1
        print(f"{self.name} retrying, attempt {self.retries}")

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "state": self.state.name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration.total_seconds() if self.duration else None,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "retries": self.retries
        }

def task(max_retries=3, delay=1, id=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            task_result = TaskResult(func.__name__)
            input_data = args if args else kwargs
            task_result.start(input_data)
            
            for attempt in range(max_retries):
                try:
                    # Execute the task
                    result = await func(*args, **kwargs)
                    
                    # Capture the output data and mark task as complete
                    task_result.complete(result)
                    await save_task_result(task_result.to_dict())
                    return task_result, result
                except Exception as e:
                    task_result.increment_retries()
                    task_result.fail(str(e))
                    await save_task_result(task_result.to_dict())
                    traceback.print_exc()
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)  # Delay before retrying
                        task_result.state = TaskState.RUNNING
            return task_result, None
        return wrapper
    return decorator