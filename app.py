import streamlit as st
import os
import sys
from langchain.agents import create_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from tools import search_tool, wiki_tool, save_tool

# 1. Page Configuration (Must be the very first Streamlit command)
st.set_page_config(page_title="Electronics Expert AI", page_icon="⚡")

# 2. API Key Bridge
# Priority: Streamlit Secrets (Web) -> Environment Variable (Local)
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if api_key:
    os.environ["GROQ_API_KEY"] = api_key
else:
    st.error("🔑 GROQ_API_KEY not found! Please add it to Streamlit Secrets.")
    st.stop()

# 3. Initialize the Agent (Stored in session_state to prevent re-loading)
if "agent" not in st.session_state:
    try:
        st.session_state.agent = create_agent(
            model="groq:llama-3.3-70b-versatile",
            tools=[search_tool, wiki_tool, save_tool],
            system_prompt="You are a Senior Electronics Engineer. Use your tools to provide deep technical circuit verification and pinout analysis."
        )
    except Exception as e:
        st.error(f"⚠️ Failed to connect to AI Brain: {e}")
        st.stop()

# 4. UI Elements
st.title("🔬 Electronics Engineering Agent")
st.markdown("Analyze circuits, pinouts, and components in real-time.")

# Setup Chat History
history = StreamlitChatMessageHistory(key="chat_messages")

# Display existing chat messages
for msg in history.messages:
    st.chat_message(msg.type).write(msg.content)

# 5. Chat Input & Processing
if prompt := st.chat_input("Ask about circuits, components, or datasheets..."):
    
    # Show user message
    st.chat_message("user").write(prompt)

    # Process AI response
    with st.chat_message("assistant"):
        try:
            with st.status("Engineer is analyzing...", expanded=True) as status:
                # We pass the conversation history + the new prompt
                result = st.session_state.agent.invoke(
                    {"messages": history.messages + [("user", prompt)]}
                )
                
                # Extract response text
                full_response = result["messages"][-1].content
                
                # Update history manually
                history.add_user_message(prompt)
                history.add_ai_message(full_response)
                
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            st.write(full_response)
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {e}")