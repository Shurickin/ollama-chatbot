import re
import json
from typing import List
from llm_client import openai_client
from database import get_connection

# Split the text into units (words, in this case)
def word_splitter(source_text: str) -> List[str]:
    source_text = re.sub(r"\s+", " ", source_text)  # Replace multiple whitespces
    return re.split(r"\s", source_text)  # Split by single whitespace

def get_chunks_fixed_size_with_overlap(text: str, chunk_size: int, overlap_fraction: float = 0.2) -> List[str]:
    text_words = word_splitter(text)
    overlap_int = int(chunk_size * overlap_fraction)
    chunks = []
    for i in range(0, len(text_words), chunk_size):
        chunk_words = text_words[max(i - overlap_int, 0): i + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
    return chunks

def save_to_sqlite(chunks, embeddings, source):
    conn = get_connection()
    cursor = conn.cursor()
    for chunk, embedding in zip(chunks, embeddings):
        cursor.execute(
            """
            INSERT INTO embeddings (chunk, embedding, source)
            VALUES (?, ?, ?)
            """,
            (chunk, json.dumps(embedding), source)
        )

    conn.commit()
    conn.close()

def delete_ALL_embeddings():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM embeddings")

    conn.commit()
    conn.close()

def delete_table(table):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {table}")

    conn.commit()
    conn.close()

def load_embeddings(source=None):
    conn = get_connection()
    cursor = conn.cursor()
    if source:
        cursor.execute(
            """
            SELECT chunk, embedding
            FROM embeddings
            WHERE source = ?
            """,
            (source,)
        )
    else:
        cursor.execute(
            """
            SELECT chunk, embedding
            FROM embeddings
            """
        )

    rows = cursor.fetchall()

    embeddings = []

    for chunk, embedding in rows:
        embeddings.append({
            "chunk": chunk,
            "embedding": embedding
        })
    
    conn.close()

    return embeddings

def get_all_sources():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DISTINCT source
        FROM embeddings
        """
    )

    rows = cursor.fetchall()

    sources = []

    for source in rows:
        sources.append({"source": source[0]})

    conn.close()

    return sources

def create_conversations_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        conversation_id TEXT NOT NULL,
        title TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def create_messages_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    #-- ID will hold the Auth Provider's UID (e.g., "AI938fksj...")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,          
        email TEXT UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def create_embedding_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk TEXT NOT NULL,
        embedding TEXT NOT NULL,
        source TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # delete_ALL_embeddings()
    # delete_table("messages")
    # create_messages_table()
    # create_conversations_table()
    # create_embedding_table()
    create_users_table()

    # with open("halo_article.txt", "r", encoding="utf-8") as f:
    #     text = f.read()

    # chunks = get_chunks_fixed_size_with_overlap(
    #     text,
    #     chunk_size=100,
    #     overlap_fraction=0.1
    # )

    # doc_embeddings = [
    #     item.embedding
    #     for item in openai_client.embeddings.create(
    #         model="embeddinggemma",
    #         input=chunks
    #     ).data
    # ]

    # save_to_sqlite(chunks, doc_embeddings, "halo_article.txt")
