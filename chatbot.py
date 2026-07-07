from openai import OpenAI

def append_msg(messages, role, content):
    messages.append({
        "role": role,
        "content": content
    })

instructions = "You are a simple, multi-turn chatbot like ChatGPT or Grok. Answer the users' questions to the best of your ability. You can fully access every message provided in the conversation history. When asked about previous messages, answer using the conversation history instead of claiming you cannot remember. Only say you don't know if the information is genuinely absent from the provided history."

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',  # required but ignored
)

messages = []

while True:
    user_msg = input("User: ")

    if user_msg.lower() in ["exit", "quit"]:
        break
    elif user_msg.lower() == "/reset":
        messages = []
        continue

    append_msg(messages, "user", user_msg)

    stream = client.responses.create(
        model='llama3',
        instructions=instructions,
        input=messages,
        stream=True,
    )

    usage = ""
    print("\n")
    print("Assistant: ", end="", flush=True)
    assistant_msg = ""
    for event in stream:
        # Handle text deltas
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
            assistant_msg += event.delta
        elif event.type == "response.completed":
            usage = event.response.usage

    append_msg(messages, "assistant", assistant_msg)
    print("\n")
    print(usage)