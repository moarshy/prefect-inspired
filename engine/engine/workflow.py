import functools
import traceback
from datetime import datetime
from engine.task import TaskState
from engine.utils import save_workflow_result, get_logger

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

    def add_task(self, task_func, task_id, *args):
        result = task_func(task_id, *args)
        logger.debug(f"Task function return value: {result}")
        task_result, result = result  # Ensure it returns a tuple
        self.tasks.append((task_func, task_id, args))
        self.workflow_result.add_task_result(task_result)
        if task_result.state == TaskState.FAILED:
            raise Exception(task_result.error_message)
        return result

    def run(self):
        try:
            self.workflow_result.start()
            for task_func, task_id, args in self.tasks:
                result = task_func(task_id, *args)
                task_result, result = result  # Ensure it returns a tuple
                self.workflow_result.add_task_result(task_result)
                if task_result.state == TaskState.FAILED:
                    self.workflow_result.fail(task_result.error_message)
                    break
            else:
                self.workflow_result.complete()
        except Exception as e:
            self.workflow_result.fail(str(e))
        finally:
            save_workflow_result(self.workflow_result)

def workflow(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            job_id = kwargs.get('job_id')  # Extract job_id from kwargs
            wf = Workflow(name, job_id)
            try:
                # Start the workflow
                wf.workflow_result.start()
                # Execute the workflow function
                func(wf, *args, **kwargs)
                # Complete the workflow
                wf.workflow_result.complete()
            except Exception as e:
                wf.workflow_result.fail(str(e))
                traceback.print_exc()
            finally:
                save_workflow_result(wf.workflow_result)
        return wrapper
    return decorator