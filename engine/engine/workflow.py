import logging
import functools
from datetime import datetime

logger = logging.getLogger(__name__)

from engine.db import (
    save_workflow_result,
    create_workflow_status,
    update_workflow_status
)
from engine.task import TaskState
from engine.utils import get_logger

logger = get_logger()

class WorkflowResult:
    def __init__(self, name, job_id):
        self.name = name
        self.job_id = job_id
        self.state = TaskState.PENDING
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.tasks = []
        self.error_message = None

    def start(self):
        self.state = TaskState.RUNNING
        self.start_time = datetime.now()
        print(f"Workflow {self.name} (ID: {self.job_id}) state: {self.state}")

    def complete(self):
        self.state = TaskState.SUCCESS
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        print(f"Workflow {self.name} (ID: {self.job_id}) state: {self.state}, Duration: {self.duration}")

    def fail(self, error_message):
        self.state = TaskState.FAILED
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        self.error_message = error_message
        print(f"Workflow {self.name} (ID: {self.job_id}) state: {self.state}, Error: {self.error_message}")

    def add_task_result(self, task_result):
        self.tasks.append(task_result.to_dict())

    def to_dict(self):
        return {
            "name": self.name,
            "job_id": self.job_id,
            "state": self.state.name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration.total_seconds() if self.duration else None,
            "tasks": self.tasks,
            "error_message": self.error_message
        }

class Workflow:
    def __init__(self, name, workflow_id):
        self.name = name
        self.workflow_result = WorkflowResult(name, workflow_id)
        self.tasks = []

    def add_task(self, task_func, *args):
        self.tasks.append((task_func, args))

    async def run(self):
        try:
            self.workflow_result.start()
            await create_workflow_status(self.workflow_result.job_id, "Starting workflow")
            num_tasks = len(self.tasks)
            previous_result = None
            for i, (task_func, args) in enumerate(self.tasks):
                if previous_result is not None:
                    args = (previous_result, *args)
                progress = f"{i + 1} of {num_tasks} task. Running"
                logger.info(f"Progress: {progress}")
                try:
                    await update_workflow_status(self.workflow_result.job_id, progress)
                except Exception as e:
                    logger.error(f"Failed to update workflow status: {e}")
                task_result, result = await task_func(*args)
                progress = f"{i + 1} of {num_tasks} task. Completed"
                try:
                    await update_workflow_status(self.workflow_result.job_id, progress)
                except Exception as e:
                    logger.error(f"Failed to update workflow status: {e}")
                self.workflow_result.add_task_result(task_result)
                if task_result.state == TaskState.FAILED:
                    self.workflow_result.fail(task_result.error_message)
                    break
                previous_result = result["response"]
            else:
                self.workflow_result.complete()
        except Exception as e:
            self.workflow_result.fail(str(e))
        finally:
            try:
                await save_workflow_result(self.workflow_result.to_dict())
            except Exception as e:
                logger.error(f"Failed to save workflow result: {e}")

def workflow(name):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            job_id = kwargs.get('job_id')
            wf = Workflow(name, job_id)
            await func(wf, *args, **kwargs)
            await wf.run()
        return wrapper
    return decorator
