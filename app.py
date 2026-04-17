import sys
print(f"DEBUG: Python version {sys.version}")
print(f"DEBUG: Installed packages: {[p for p in sys.modules.keys() if 'langchain' in p]}")

import streamlit as st
# ... your other imports
import streamlit as st
import os

# This part bridges Streamlit Secrets to the Agent's brain
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
else:
    st.error("GROQ_API_KEY not found in Streamlit Secrets!")
    st.stop()
from langchain.agents import create_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_groq import ChatGroq
from tools import search_tool, wiki_tool, save_tool
# 1. Force the environment variable so the Agent can "see" the key
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# 2. Initialize the Agent in the session state (so it doesn't reload every click)
if "agent" not in st.session_state:
    try:
        st.session_state.agent = create_agent(
            model="groq:llama-3.3-70b-versatile",
            tools=[search_tool, wiki_tool, save_tool],
            system_prompt="You are a Senior Electronics Engineer. Help the user with circuit design and component selection."
        )
    except Exception as e:
        st.error(f"Failed to connect to AI Brain: {e}")
        st.stop() # Stops the app here so it doesn't crash further down

# Only try to load dotenv if we are running locally
# Streamlit Cloud handles the keys automatically from 'Secrets'
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

# Now get the key from either .env (local) or Secrets (cloud)
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found! Please add it to Streamlit Secrets.")
    st.stop()


load_dotenv()

# 1. Page Configuration
st.set_page_config(page_title="Electronics Expert AI", page_icon="⚡")
st.title("🔬 Electronics Engineering Agent")
st.markdown("Analyze circuits, pinouts, and components in real-time.")

# 2. Setup Chat History (Stored in the web session)
history = StreamlitChatMessageHistory(key="chat_messages")

# 3. Initialize the Agent (Options 2 - Modern 1.0)
if "agent" not in st.session_state:
    st.session_state.agent = create_agent(
        model="groq:llama-3.3-70b-versatile",
        tools=[search_tool, wiki_tool, save_tool],
        system_prompt="You are a Principal Hardware Engineer. Provide deep technical circuit verification."
    )

# 4. Display Chat History
for msg in history.messages:
    st.chat_message(msg.type).write(msg.content)

# 5. User Input
if prompt := st.chat_input("Enter component (e.g., 'ESP32 Pinout'):"):
    # Display user message
    st.chat_message("user").write(prompt)
    
    # Process with Agent
    with st.chat_message("assistant"):
        st.write("Checking datasheets and specs...")
        # Invoke agent with history
        response = st.session_state.agent.invoke({"messages": history.messages + [("user", prompt)]})
        output = response["messages"][-1].content
        st.write(output)
        
        # Add to session history
        history.add_user_message(prompt)
        history.add_ai_message(output)
        # Inside app.py, where you create the agent:
if "agent" not in st.session_state:
    try:
        # Use the string-based model identifier for 2026 Groq
        st.session_state.agent = create_agent(
            model="groq:llama-3.3-70b-versatile",
            tools=[search_tool, wiki_tool, save_tool],
            system_prompt="You are a Senior Electronics Engineer. Use your tools to analyze circuits."
        )
    except Exception as e:
        st.error(f"Waiting for Groq connection... {e}")
        st.stop()