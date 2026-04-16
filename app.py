import streamlit as st
import os
from dotenv import load_dotenv


from dotenv import load_dotenv
from langchain.agents import create_agent  # Modern 1.0 import
from tools import search_tool, wiki_tool, save_tool



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