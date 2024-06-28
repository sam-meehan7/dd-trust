# openai_assistant_project/assistant.py
from openai import OpenAI
import json
import os
import time
import os


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def show_json(obj):
    print(json.loads(obj.model_dump_json()))

thread = client.beta.threads.create()
# show_json(thread)

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I have recieved a text with a link to send payment",
)
# show_json(message)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=os.getenv("ASSISTANT_ID"),
)

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

run = wait_on_run(run, thread)

messages = client.beta.threads.messages.list(thread_id=thread.id)
show_json(messages)




