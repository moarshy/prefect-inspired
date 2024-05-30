from engine.workflow import workflow
from engine.utils import get_logger, save_to_node, upload_to_ipfs
import asyncio
from engine.workflow import workflow
from chat.run import run as chat_run
from dotenv import load_dotenv

logger = get_logger()
load_dotenv()

@workflow(name="multichat")
async def multichat(wf, prompt, job_id):
    logger.info("multichat")
    wf.add_task(chat_run, prompt)
    wf.add_task(chat_run)
    wf.add_task(chat_run)

    return wf

def main():
    asyncio.run(multichat(prompt="hello", job_id="456"))

if __name__ == "__main__":
    main()