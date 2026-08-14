import os
from openai import OpenAI

# For Production use with Render, the API key is set in the environment variable OPENROUTER_API_KEY.
openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# ---------- For Local Testing ----------

# openai_client = OpenAI(
#     base_url="http://localhost:11434/v1",  # or OpenAI cloud if you switch later
#     api_key="ollama"
# )