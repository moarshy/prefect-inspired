from surrealdb import Surreal


async def save_task_result(task_result):
    async with Surreal("ws://localhost:8000/rpc") as db:
            await db.signin({"user": "root", "pass": "root"})
            await db.use("test", "test")
            await db.create(f'task_results:{task_result["id"]}', task_result)

async def save_workflow_result(workflow_result):
    async with Surreal("ws://localhost:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")    
        await db.create(f'workflow_results:{workflow_result["job_id"]}', workflow_result)

async def create_workflow_status(job_id, status):
    async with Surreal("ws://localhost:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        await db.create(f'workflow_status:{job_id}', {"status": status})

async def update_workflow_status(job_id, status):
    print(job_id, status)
    async with Surreal("ws://localhost:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        await db.update(f'workflow_status:{job_id}', {"status": status})