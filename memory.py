from database import get_connection

conversation = {}

def get_history(session_id):
    if session_id not in conversation:
        conversation[session_id] = load_from_sqlite(session_id)

    return conversation[session_id]

def save_message(session_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages (conversation_id, role, content)
        VALUES (?, ?, ?)
        """,
        (session_id, role, content)
    )
    conn.commit()
    conn.close()

def insert_convo(user_id, conversation_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (user_id, conversation_id)
        VALUES (?, ?)
        """,
        (user_id, conversation_id)
    )
    conn.commit()
    conn.close()

def add_title(conversation_id, title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE conversations
        SET title=?
        WHERE conversation_id=?
        """,
        (title, conversation_id)
    )

    print(f"Rows updated: {cursor.rowcount}")
    conn.commit()
    conn.close()

def insert_user(user_id, email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (id, email)
        VALUES (?, ?)
        """,
        (user_id, email)
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
        WHERE conversation_id = ?
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

def get_conversations(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT conversation_id, title
        FROM conversations
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    conversations = []

    for conversation_id, title in rows:
        conversations.append({
            "conversation_id": conversation_id,
            "title": title
        })

    conn.close()
    
    return conversations

def deleteConvo(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        DELETE FROM conversations WHERE conversation_id = ?
        """,
        (conversation_id,)
    )
    conn.commit()
    conn.close()
    


# The old file that would be reset when the server is closed

# conversations = {}

# def load(session_id):
#     return conversations.get(session_id, [])

# def save(session_id, messages):
#     conversations[session_id] = messages