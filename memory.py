from database import get_connection

conversations = {}

def get_history(session_id):
    if session_id not in conversations:
        conversations[session_id] = load_from_sqlite(session_id)

    return conversations[session_id]

def save_message(session_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages (session_id, role, content)
        VALUES (?, ?, ?)
        """,
        (session_id, role, content)
    )
    conn.commit()
    conn.close()

def load_from_sqlite(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id
        """,
        (session_id,)
    )

    rows = cursor.fetchall()

    history = []

    for role, content in rows:
        history.append({
            "role": role,
            "content": content
        })

    conn.close()
    
    return history


# The old file that would be reset when the server is closed

# conversations = {}

# def load(session_id):
#     return conversations.get(session_id, [])

# def save(session_id, messages):
#     conversations[session_id] = messages