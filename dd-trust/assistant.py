# openai_assistant_project/assistant.py
from openai import OpenAI

def interact_with_assistant(client, assistant_id, user_input):
    response = client.beta.assistants.messages.create(
        assistant_id=assistant_id,
        message={'role': 'user', 'content': user_input}
    )
    return response['choices'][0]['message']['content']

def main():
    api_key = ''  # Replace with your actual OpenAI API key
    assistant_id = ""  # Replace with your actual assistant ID

    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = interact_with_assistant(client, assistant_id, user_input)
        print(f"Assistant: {response}")

if __name__ == "__main__":
    main()
