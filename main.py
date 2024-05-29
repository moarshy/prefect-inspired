import os
import json
import functools
import traceback
import time
from datetime import datetime
from enum import Enum, auto


def save_task_result(task_result):
    results_dir = "task_results"
    os.makedirs(results_dir, exist_ok=True)
    
    file_path = os.path.join(results_dir, f"{task_result.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(file_path, "w") as file:
        json.dump(task_result.to_dict(), file, indent=4)

class TaskState(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()

class TaskResult:
    def __init__(self, name):
        self.name = name
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
            "state": self.state.name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration.total_seconds() if self.duration else None,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "retries": self.retries
        }

def task(max_retries=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            task_result = TaskResult(func.__name__)
            input_data = args if args else kwargs
            task_result.start(input_data)
            
            for attempt in range(max_retries):
                try:
                    # Execute the task
                    result = func(*args, **kwargs)
                    
                    # Capture the output data and mark task as complete
                    task_result.complete(result)
                    return task_result, result
                except Exception as e:
                    task_result.increment_retries()
                    task_result.fail(str(e))
                    traceback.print_exc()
                    if attempt < max_retries - 1:
                        time.sleep(delay)  # Delay before retrying
                        task_result.state = TaskState.RUNNING
                finally:
                    # Save the task result to a file after each attempt
                    save_task_result(task_result)
            return task_result, None
        return wrapper
    return decorator

class WorkflowResult:
    def __init__(self, name):
        self.name = name
        self.state = TaskState.PENDING
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.tasks = []
        self.error_message = None

    def start(self):
        self.state = TaskState.RUNNING
        self.start_time = datetime.now()
        print(f"Workflow {self.name} state: {self.state}")

    def complete(self):
        self.state = TaskState.SUCCESS
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        print(f"Workflow {self.name} state: {self.state}, Duration: {self.duration}")

    def fail(self, error_message):
        self.state = TaskState.FAILED
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        self.error_message = error_message
        print(f"Workflow {self.name} state: {self.state}, Error: {self.error_message}")

    def add_task_result(self, task_result):
        self.tasks.append(task_result.to_dict())

    def to_dict(self):
        return {
            "name": self.name,
            "state": self.state.name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration.total_seconds() if self.duration else None,
            "tasks": self.tasks,
            "error_message": self.error_message
        }

def save_workflow_result(workflow_result):
    results_dir = "workflow_results"
    os.makedirs(results_dir, exist_ok=True)
    
    file_path = os.path.join(results_dir, f"{workflow_result.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(file_path, "w") as file:
        json.dump(workflow_result.to_dict(), file, indent=4)

class Workflow:
    def __init__(self, name):
        self.name = name
        self.workflow_result = WorkflowResult(name)
        self.tasks = []

    def add_task(self, task_func, *args):
        self.tasks.append((task_func, args))

    def run(self):
        self.workflow_result.start()
        try:
            for task, args in self.tasks:
                task_result, result = task(*args)
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

@task(max_retries=3, delay=2)
def extract_data():
    # Simulate data extraction
    data = {"value": 42}
    return data

@task(max_retries=3, delay=2)
def transform_data(data):
    # Simulate data transformation
    if data is None:
        raise ValueError("No data to transform")
    transformed_data = data["value"] * 2
    return transformed_data

@task(max_retries=3, delay=2)
def load_data(transformed_data):
    # Simulate data loading
    if transformed_data is None:
        raise ValueError("No data to load")
    print(f"Loading data: {transformed_data}")

def main():
    # Create a workflow
    workflow = Workflow("ETL Workflow")
    
    # Add tasks to the workflow
    workflow.add_task(extract_data)
    workflow.add_task(transform_data, {"value": 42})
    workflow.add_task(load_data, 84)
    
    # Run the workflow
    workflow.run()

if __name__ == "__main__":
    main()