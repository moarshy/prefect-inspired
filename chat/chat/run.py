import openai
from engine.task import task
from engine.utils import get_logger

logger = get_logger()


@task()
def run(prompt):
    client = openai.OpenAI()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    logger.info(messages)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.0,
    )
    response = response.choices[0].message.content

    return {
        "response": response,
    }

