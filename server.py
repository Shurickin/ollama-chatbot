import uuid
import json
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from typing import Optional

from llm_client import openai_client
from memory import get_history
from memory import save_message
from tools import add
from tools import get_weather
from tools import tools
from rag import search

# Defines what the client must send
class QuestionRequest(BaseModel):
    session_id: str
    question: str

# class ToolRouterResponse(BaseModel):
#     needs_tool: bool
#     tool_name: Optional[str] = None
#     tool_arguments: Optional[str] = None

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

app = FastAPI()

client = openai_client

# print(tools)

@app.post("/ask")
def ask_question(request: QuestionRequest):

    # history = conversations.get(str(request.session_id), [])
    history = get_history(request.session_id)

    history.append({
        "role": "user",
        "content": request.question
    })

    save_message(
        request.session_id,
        "user",
        request.question
    )

    # Route to determine tool use
    router_response = client.responses.create(
        model="qwen3.5",
        input=history,
        instructions = system_prompt,
        tools = tools,
        # format = ToolRouterResponse.model_json_schema()
    )

    print(router_response.model_dump_json(indent=2))

    llama_prompt = llama_system_prompt

    for item in router_response.output:
        if item.type == "function_call":
            if item.name == "add":
                args = json.loads(item.arguments)
                result = add(args["a"], args["b"])
                print(result)
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
                print(result)

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

            
            
            
            # llama_prompt += addition
    results = search(request.question, top_k=3)

    if results[0][0] > 0.45:
        use_context = True
    else:
        use_context = False
    
    if use_context:
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

    llama_response = client.responses.create(
        model = "llama3",
        input = history,
        instructions = llama_prompt,
    )

    save_message(
        request.session_id,
        "assistant",
        llama_response.output_text
    )

    print(llama_response.model_dump_json(indent=2))

    history.append({
        "role": "assistant",
        "content": llama_response.output_text
    })

    # save(str(request.session_id), history)

    return {
        "question": request.question,
        "answer": llama_response.output_text
    }