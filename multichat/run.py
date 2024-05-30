from engine.workflow import workflow
from engine.utils import get_logger, save_to_node, upload_to_ipfs
from chat.run import run as chat_run
from dotenv import load_dotenv

logger = get_logger()
load_dotenv()

@workflow(name="multichat")
def multichat(wf, prompt, job_id):
    logger.info("multichat")
    out1 = wf.add_task(chat_run, prompt)
    logger.info(out1)
    out2 = wf.add_task(chat_run, out1["response"])  
    logger.info(out2)

    # depending on things, save to node or ipfs
    save_to_node()
    upload_to_ipfs()

    return out2

def main():
    multichat(prompt="hello", job_id="123")

if __name__ == "__main__":
    main()
