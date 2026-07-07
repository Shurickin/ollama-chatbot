import requests
import uuid

session_id = str(uuid.uuid4())
# session_id = "ec49aa29-3662-4bf9-afb6-a55aa7c75a6f"

url = "http://127.0.0.1:8000/ask"

print("Welcome to Jordan's Local AI! Ask any question you would like!\n\n")

while True:
    user_msg = input("User: ")
    print()
    if user_msg.lower() in ["exit", "quit"]:
        break
    elif user_msg.lower() == "/reset":
        messages = []
        continue

    #append_msg(messages, "user", user_msg)

    payload = {
        "session_id": session_id,
        "question": user_msg
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
            txt = response.json()["answer"]
            print(f"Assistant: {txt}\n")
    else:
        print(f"Error: {response.status_code}")

    # stream = client.responses.create(
    #     model='llama3',
    #     instructions=instructions,
    #     input=messages,
    #     stream=True,
    # )

    # usage = ""
    # print("\n")
    # print("Assistant: ", end="", flush=True)
    assistant_msg = ""
    # for event in stream:
    #     # Handle text deltas
    #     if event.type == "response.output_text.delta":
    #         print(event.delta, end="", flush=True)
    #         assistant_msg += event.delta
    #     elif event.type == "response.completed":
    #         usage = event.response.usage

    # append_msg(messages, "assistant", assistant_msg)
    # print("\n")
    # print(usage)