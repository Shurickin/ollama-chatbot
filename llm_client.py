from openai import OpenAI

openai_client = OpenAI(
    base_url="http://localhost:11434/v1",  # or OpenAI cloud if you switch later
    api_key="ollama"
)