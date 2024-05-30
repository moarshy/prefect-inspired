import os
import json
import logging
from datetime import datetime


def save_workflow_result(workflow_result):
    results_dir = "workflow_results"
    os.makedirs(results_dir, exist_ok=True)
    
    file_path = os.path.join(results_dir, f"{workflow_result.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(file_path, "w") as file:
        json.dump(workflow_result.to_dict(), file, indent=4)

def save_task_result(task_result):
    results_dir = "task_results"
    os.makedirs(results_dir, exist_ok=True)
    
    file_path = os.path.join(results_dir, f"{task_result.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(file_path, "w") as file:
        json.dump(task_result.to_dict(), file, indent=4)

def update_db(**kwargs):
    print("Updating database...")

def save_to_node(**kwargs):
    print("Saving to node...")

def upload_to_ipfs(**kwargs):
    print("Uploading to IPFS...")

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Check if handlers are already added
        logger.setLevel(logging.DEBUG)
        # Create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # Add formatter to ch
        ch.setFormatter(formatter)
        # Add ch to logger
        logger.addHandler(ch)
    return logger