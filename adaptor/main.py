import json
import os
import sqlite3
import time
from collections.abc import Iterator
from datetime import datetime
from typing import Any

import streamlit as st
from ollama import ChatResponse, Client
from PIL import Image
from scripts.user import check_username, init_db_user, signup_user, singin_user
from scripts.utils import config_args, logger

st.set_page_config(
    page_title="Adaptor",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initial folder creation
if not os.path.exists("adaptor/data/history"):
    os.makedirs("adaptor/data/history")

init_db_user()

# Session States
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "session" not in st.session_state:
    st.session_state["session"] = datetime.now().strftime("%y-%m-%d_%H-%M-%S")

if "chosen_session" not in st.session_state:
    st.session_state["chosen_session"] = ""

if "initial" not in st.session_state:
    st.session_state["initial"] = True

if "image_uploaded" not in st.session_state:
    st.session_state["image_uploaded"] = False

if "signedin" not in st.session_state:
    st.session_state["signedin"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None

if "username_exist" not in st.session_state:
    st.session_state["username_exist"] = False

if "wrong_information" not in st.session_state:
    st.session_state["wrong_information"] = False


# Functions
@st.cache_resource
def conversation(
    prompt: str,
    use_image: bool,
    image_path: str,
    history: list[Any],
    max_retries: int = 3,
    retry_delay: int = 1,
) -> Iterator[ChatResponse] | None:
    """Initialize Ollama system with streaming response"""
    if use_image:
        messages = [{"role": "user", "content": prompt, "images": [image_path]}]
    else:
        messages = [{"role": "user", "content": prompt}]
    for attempt in range(max_retries):
        try:
            stream = Client("http://ollama_adaptor:11434").chat(
                config_args.model, messages=history + messages, stream=True, think=True
            )
            return stream

        except Exception as e:
            logger.warning(
                f"Initialize conversation error attempt {attempt + 1}: {str(e)}"
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise


def connect_to_db():
    """Initialize connection with conversation database"""
    try:
        return sqlite3.connect(
            f"adaptor/data/history/{st.session_state['username']}_conversations.db"
        )
    except Exception as e:
        logger.warning(f"Failed to connect db: {e}")


def init_db():
    """Create table within database to store conversations"""
    if conn := connect_to_db():
        c = conn.cursor()
        exec_query = """CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY,
        session_id TEXT NOT NULL,
        messages TEXT NOT NULL
        )"""
        c.execute(exec_query)
        conn.commit()
        conn.close()
    else:
        raise


def start_conversation(session_id: str):
    """Add first empty values to start new conversation with session id"""
    initial_message = json.dumps([])

    if conn := connect_to_db():
        c = conn.cursor()
        exec_query = "INSERT INTO conversations (session_id, messages) VALUES (?, ?)"
        c.execute(exec_query, (session_id, initial_message))
        conn.commit()
        conn.close()


def add_message(session_id: str, message_history: list[Any]):
    """Add messages to the database based on session id"""
    if conn := connect_to_db():
        c = conn.cursor()

        # Get current messages
        c.execute(
            "SELECT messages FROM conversations WHERE session_id = ?", (session_id,)
        )
        row = c.fetchone()

        if row:
            messages = json.loads(row[0])
            for message in message_history:
                messages.append(message)
            new_messages = json.dumps(messages)
            exec_query = "UPDATE conversations SET messages = ? WHERE session_id = ?"
            c.execute(
                exec_query,
                (new_messages, session_id),
            )
            conn.commit()

        conn.close()


def get_conversation(session_id: str) -> list[dict | Any] | Any:
    """ "Retrieve conversation from data based on session id"""
    if conn := connect_to_db():
        c = conn.cursor()
        exec_query = "SELECT messages FROM conversations WHERE session_id = ?"
        c.execute(exec_query, (session_id,))
        row = c.fetchone()

        conn.close()
        return json.loads(row[0]) if row else []


def get_recent_conversations(limit: int = 10) -> list[Any] | Any:
    """Retrieve information about recent 10 conversations from database"""
    if conn := connect_to_db():
        c = conn.cursor()
        c.execute(
            "SELECT session_id, messages FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = c.fetchall()

        result = []
        for row in rows:
            try:
                messages = json.loads(row[1])
                result.append({"session_id": row[0], "messages": messages})
            except Exception:
                continue

        return result


def load_captions() -> list:
    """Loads captions for Chat History section"""
    captions_list = []
    history_files = get_recent_conversations()
    for history_file in history_files:
        if len(history_file["messages"]) > 0:
            captions_list.append(history_file["messages"][0]["content"][:25])
        else:
            captions_list.append("New conversation")
    return captions_list


# Login dialog
@st.dialog("Welcome to Adaptor", dismissible=False)
def signup_signin():
    global USER
    signup_tab, signin_tab = st.tabs(["Sign Up", "Sign In"])

    with signup_tab:
        if st.session_state["username_exist"]:
            st.error("Username already exist")
        signup_username = st.text_input("Username", key="signup_username")
        signup_password = st.text_input(
            "Password", key="signup_password", type="password"
        )
        if st.button("Sign Up"):
            if signup_username and signup_password:
                if check_username(signup_username):
                    signup_user(signup_username, signup_password)
                    st.session_state["signedin"] = True
                    st.session_state["username"] = signup_username
                    st.rerun()
                else:
                    st.session_state["signedin"] = False
                    st.session_state["username_exist"] = True
                    st.rerun()
            else:
                st.write("Please fill both fields.")
                st.session_state["signedin"] = False
                st.rerun()

    with signin_tab:
        if st.session_state["wrong_information"]:
            st.error("Please check username and password")
        signin_username = st.text_input("Username", key="signin_username")
        signin_password = st.text_input(
            "Password", key="signin_password", type="password"
        )
        if st.button("Sign In"):
            if signin_username and signin_password:
                if singin_user(signin_username, signin_password):
                    st.session_state["signedin"] = True
                    st.session_state["username"] = signin_username
                    st.rerun()
                else:
                    logger.debug("Signin failed")
                    st.session_state["signedin"] = False
                    st.session_state["wrong_information"] = True
                    st.rerun()
            else:
                st.write("Please fill both fields.")
                st.session_state["signedin"] = False
                st.rerun()


if not st.session_state["signedin"]:
    signup_signin()

else:
    if st.session_state["initial"]:
        init_db()
        start_conversation(st.session_state["session"])
        st.session_state["initial"] = False

    # Sidebar
    with st.sidebar:
        with st.container(height=220):
            image_byte = st.file_uploader(
                "Choose an image for chat",
                type=["png", "jpg", "jpeg"],
                help="You can choose an image to interact over chat. Image can be 'png', 'jpg', 'jpeg'.",
            )
            if image_byte:
                image = Image.open(image_byte)
                image.save("adaptor/data/image.jpg")
                st.session_state["image_uploaded"] = True
        with st.container(height=320):
            st.session_state["chosen_session"] = st.radio(
                "Chat History",
                [conv["session_id"] for conv in get_recent_conversations()],
                width="stretch",
                help="Sorting is based on date and time (year-month-day_hour-minute-second). If you do not receive any answer, make sure to repeat your prompt.",
                captions=load_captions(),
            )

    # Chat interface
    for message in get_conversation(st.session_state["chosen_session"]):
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Type here..."):
        # User
        with st.chat_message("user"):
            st.write(prompt)
            st.session_state["messages"].append({"role": "user", "content": prompt})

        # Assistant
        with st.chat_message("assistant"):
            thinking_content = ""
            response_content = ""
            with st.status("Thinking...", expanded=False) as status:
                thinking_placeholder = st.empty()
            response_placeholder = st.empty()
            stream = conversation(
                prompt,
                use_image=st.session_state["image_uploaded"],
                image_path="adaptor/data/image.jpg",
                history=get_conversation(st.session_state["chosen_session"]),
            )
            if stream:
                for chunk in stream:
                    if chunk.message.thinking:
                        thinking_content += chunk.message.thinking
                        thinking_placeholder.markdown(thinking_content)
                    elif chunk.message.content:
                        response_content += chunk.message.content
                        response_placeholder.markdown(response_content)
                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": response_content,
                        "thinking": thinking_content,
                    },
                )
        add_message(st.session_state["chosen_session"], st.session_state["messages"])
