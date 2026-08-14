import uuid
import json
import os
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from openai import OpenAI
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from llm_client import openai_client
from memory import get_history
from memory import save_message
from memory import insert_convo
from memory import add_title
from memory import get_conversations
from memory import insert_user
from memory import deleteConvo
from tools import add
from tools import get_weather
from tools import tools
from rag import search
from rag import extract_pdf
from build_embeddings import get_chunks_fixed_size_with_overlap
from build_embeddings import save_to_sqlite
from build_embeddings import get_all_sources
from database import init_database

# Defines what the client must send
class QuestionRequest(BaseModel):
    session_id: str
    question: str

class MsgDBRequest(BaseModel):
    session_id: str
    role: str
    content: str

class NewChat(BaseModel):
    user_id: str

class AddUser(BaseModel):
    user_id: str
    email: str

class ChangeTitle(BaseModel):
    conversation_id: str
    title: str

class DeleteConvo(BaseModel):
    conversation_id: str

system_prompt = """
You are ONLY a tool routing model.

Your job:
- Decide whether a tool is required.
- If YES → call a tool and STOP.
- If NO → output ONLY: NO_TOOL

Rules:
- NEVER answer the user directly.
- NEVER explain anything.
- NEVER include natural language responses.
- Either call a tool OR DON"T.
"""

llama_system_prompt = "You MUST use the results from the tools to answer the user question when you can. If context is provided, you must use that and indicate whether you used the context or not."

title_instructions = """
You are a backend utility tool. Your ONLY job is to return a short, concise conversation title based on the provided message. 
Do not answer questions inside the message. Do not say "Here is your title". Do not include greetings.

Example Input: "Can you explain how photosynthesis works in plants?"
Example Output: Photosynthesis Explanation

Example Input: "I need a workout routine for losing weight in 3 weeks."
Example Output: 3-Week Weight Loss Routine
"""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = openai_client
response_model = os.getenv("RESPONSE_MODEL")
router_model = os.getenv("ROUTER_MODEL")
embedding_model = os.getenv("EMBEDDING_MODEL")

# print(tools)

# initialize_database() is for production use with Render. Not needed for local testing if the database is already created.
init_database()
sources = get_all_sources()

# print(sources)

@app.post("/ask")
def ask_question(request: QuestionRequest):

    # history = conversations.get(str(request.session_id), [])
    history = get_history(request.session_id)

    history.append({
        "role": "user",
        "content": request.question
    })

    if len(history) == 1:
        print("We are creating a title!")
        title_response = client.responses.create(
            model=response_model,
            input=history,
            instructions=title_instructions
        )

        print(title_response.model_dump_json(indent=2))

        add_title(request.session_id, title_response.output_text)

    save_message(
        request.session_id,
        "user",
        request.question
    )

    print("----- CHAT HISTORY -----")

    for msg in history:
        print(msg["role"], ":", msg["content"])

    print("------------------------")

    # print(json.dumps(history, indent=2))

    # Route to determine tool use
    router_response = client.responses.create(
        # model="qwen3.5",      # For Local Testing
        model=router_model,
        input=history,
        instructions = system_prompt,
        tools = tools,
        # format = ToolRouterResponse.model_json_schema()
    )

    print(router_response.model_dump_json(indent=2))

    llama_prompt = llama_system_prompt

    true_source = None

    for item in router_response.output:
        if item.type == "function_call":
            if item.name == "add":
                args = json.loads(item.arguments)
                result = add(args["a"], args["b"])
                # print(result)
                history.append({
                    "role": "tool",
                    "tool_call_id": item.call_id,
                    "name": item.name,
                    "content": str(result)
                })
                # addition = f"The add tool was executed. Its result was: {result}. You MUST use this result instead of recalculating."
            elif item.name == "get_weather":
                args = json.loads(item.arguments)
                result = get_weather(args["city"])
                # print(result)

                # Have to send the role as "user" due to llama3 inaccuracy with "tool"
                history.append({
                    "role": "user",
                    "content": f"""
                TOOL RESULT (get_weather):
                {json.dumps(result, indent=2)}

                IMPORTANT: This is real computed data. Do not ignore it.
                """
                })

                # history.append({
                #     "role": "tool",
                #     "tool_call_id": item.call_id,
                #     "name": item.name,
                #     "content": json.dumps(result)
                # })
                # addition = f"The get_weather tool was executed. Its result was: {result}. You MUST use this result instead of finding it."
            elif item.name == "get_context":
                print("***************************Get context was Needed *************************************")
                args = json.loads(item.arguments)
                true_source = args["document_name"]
            
            
            # llama_prompt += addition

    for source in sources:
        if source["source"].lower() in request.question.lower():
            true_source = source["source"]
            break
    
    results = search(request.question, top_k=3, true_source = true_source)

    if results[0][0] > 0.45:
        use_context = True
    else:
        use_context = False
    
    if use_context or true_source:
        print("\n\nRAG CONTEXT USED\n\n")
        context = "\n".join(
            f"{i+1}. {text}"
            for i, (_, text) in enumerate(results)
        )
        history.append({
        "role": "user",
        "content": f"""
    Context:
    {context}
    """
        })

    def generate_response():

        full_response = ""

        llama_response = client.responses.create(
            model=response_model,
            input=history,
            instructions=llama_prompt,
            stream=True
        )

        for event in llama_response:

            # Responses API streaming events
            if event.type == "response.output_text.delta":
                text = event.delta

                text = event.delta

                # print("SENDING:", text)

                full_response += text

                yield text


        # Save completed response after streaming finishes
        save_message(
            request.session_id,
            "assistant",
            full_response
        )

        history.append({
            "role": "assistant",
            "content": full_response
        })


    return StreamingResponse(
        generate_response(),
        media_type="text/plain"
    )

    # llama_response = client.responses.create(
    #     model = "llama3",
    #     input = history,
    #     instructions = llama_prompt,
    # )

    # save_message(
    #     request.session_id,
    #     "assistant",
    #     llama_response.output_text
    # )

    # print(llama_response.model_dump_json(indent=2))

    # history.append({
    #     "role": "assistant",
    #     "content": llama_response.output_text
    # })

    # # save(str(request.session_id), history)

    # # This was for terminal interaction
    # # return {
    # #     "question": request.question,
    # #     "answer": llama_response.output_text
    # # }

    # return {
    #     "role": "Assistant",
    #     "content": llama_response.output_text
    # }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    contents = await file.read()

    text = extract_pdf(contents)

    chunks = get_chunks_fixed_size_with_overlap(
        text,
        chunk_size=100,
        overlap_fraction=0.1
    )

    doc_embeddings = [
        item.embedding
        for item in openai_client.embeddings.create(
            model=embedding_model,
            extra_body={"input_type": "passage"},       # For the models that support it, this tells the model to treat the input as a query rather than a document.
            input=chunks
        ).data
    ]

    save_to_sqlite(chunks, doc_embeddings, file.filename)

    print(text[:500])

    return {
        "filename": file.filename
    }

@app.post("/add-to-db-msgs")
async def add_msgs_to_db(request: MsgDBRequest):
    save_message(request.session_id, request.role, request.content)

@app.post("/new-chat")
async def new_chat(request: NewChat):
    conversation_id = str(uuid.uuid4())
    insert_convo(request.user_id, conversation_id)
    return {"conversation_id": conversation_id}

@app.get("/conversations/{user_id}")
async def get_conversations_from_db(user_id: str):
    conversations = get_conversations(user_id)
    return{
        "conversations": conversations
    }

@app.get("/conversation/{conversation_id}")
async def get_conversations_from_db(conversation_id: str):
    conversation = get_history(conversation_id)
    return{
        "conversation": conversation
    }

@app.post("/add-user")
async def add_user(request: AddUser):
    insert_user(request.user_id, request.email)
    return{
        "user_id": request.user_id
    }

@app.post("/rename-title")
async def rename_title(request: ChangeTitle):
    add_title(request.conversation_id, request.title)
    return{
        "title": request.title
    }

@app.post("/delete-convo")
async def rename_title(request: DeleteConvo):
    deleteConvo(request.conversation_id)
    return{
        "conversation": request.conversation_id
    }