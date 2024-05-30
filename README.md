# Prefect-Inspired Project Setup

This guide will help you set up a virtual environment and install the necessary dependencies for the `engine`, `chat`, and `multichat` components of the project.

## Setup Instructions

### Step 1: Create a Virtual Environment

First, create a virtual environment to isolate the project dependencies.

```sh
python -m venv venv
```

Activate the virtual environment:
```sh
source venv/bin/activate
```

### Step 2: Install engine Package
Navigate to the engine directory and install the package in editable mode:
```sh
cd engine
pip install -e .
```

### Step 3: Install chat Package
Navigate to the chat directory and install the package in editable mode:
```
cd ../chat
pip install -e .
```

### Step 4: Run the multichat Script
Navigate to the multichat directory and run the run.py script:
```sh
cd ../multichat
python run.py
```


