import streamlit as st
import os
import time
from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
from typing_extensions import override

load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class EventHandler(AssistantEventHandler):
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.text = ""
        self.started = False

    @override
    def on_text_created(self, text) -> None:
        if not self.started:
            self.text = text.value
            self.started = True
        else:
            self.text += text.value
        self.placeholder.markdown(self.text)

    @override
    def on_text_delta(self, delta, snapshot):
        self.text += delta.value
        self.placeholder.markdown(self.text)

    def on_tool_call_created(self, tool_call):
        self.text += f"\n{tool_call.type}\n"
        self.placeholder.markdown(self.text)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                self.text += delta.code_interpreter.input.value
                self.placeholder.markdown(self.text)
            if delta.code_interpreter.outputs:
                self.text += "\n\noutput >"
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        self.text += f"\n{output.logs}"
                self.placeholder.markdown(self.text)

def wait_on_run(run, thread_id):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def main():
    st.title("OpenAI Assistant Chat")

    # Initialize session state
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Create a message in the thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input,
        )

        # Stream the response
        with st.chat_message("assistant"):
            placeholder = st.empty()
            event_handler = EventHandler(placeholder)
            with client.beta.threads.runs.stream(
                thread_id=st.session_state.thread_id,
                assistant_id=os.getenv("ASSISTANT_ID"),
                event_handler=event_handler,
            ) as stream:
                stream.until_done()

            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": event_handler.text})

if __name__ == "__main__":
    main()