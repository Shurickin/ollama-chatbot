from llm_client import openai_client
import numpy as np
import json
from build_embeddings import load_embeddings
from pypdf import PdfReader
import io
import os

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search(query, top_k=3, true_source=None):
    query_embedding = openai_client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL"),
        extra_body={"input_type": "query"},     # For the models that support it, this tells the model to treat the input as a query rather than a document.
        encoding_format="float",                # Needed for NVIDIA Nemotron embeddings, which return a list of floats rather than a list of strings (base64).
        input=query
    ).data[0].embedding

    rows = load_embeddings(true_source)

    # print(rows)

    scores = []
    for row in rows:
        score = cosine_similarity(
            query_embedding,
            json.loads(row["embedding"])
        )
        scores.append((score, row["chunk"]))
    # for i, doc_vec in enumerate(doc_embeddings):
    #     score = cosine_similarity(query_embedding, doc_vec)
    #     scores.append((score, chunks[i]))

    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[:top_k]

def extract_pdf(contents):

    pdf = PdfReader(io.BytesIO(contents))

    text = ""

    for page in pdf.pages:
        text += page.extract_text()

    return text

