import streamlit as st
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

        # Create a run
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=os.getenv("ASSISTANT_ID"),
        )

        # Wait for the run to complete
        with st.spinner("Assistant is thinking..."):
            run = wait_on_run(run, st.session_state.thread_id)

        # Retrieve and display the assistant's response
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        assistant_message = next(msg for msg in messages if msg.role == "assistant")
        assistant_response = assistant_message.content[0].text.value

        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.write(assistant_response)

if __name__ == "__main__":
    main()