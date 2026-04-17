import streamlit as st
import os
from langchain.agents import create_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from tools import search_tool, wiki_tool, save_tool

# --- 1. Ultimate 2026 Import Bridge ---
# We use this to prevent the "ModuleNotFoundError" caused by Streamlit's internal changes
try:
    # Most modern 2026 Path
    from streamlit.runtime.scriptrunner_utils.script_run_context import add_script_run_context
except ImportError:
    try:
        # Late 2025 Path
        from streamlit.runtime.scriptrunner.script_run_context import add_script_run_context
    except ImportError:
        try:
            # Standard Path
            from streamlit.runtime.scriptrunner import add_script_run_context
        except ImportError:
            # Emergency Fallback
            def add_script_run_context(thread=None):
                return None

# --- 2. Page Configuration ---
# This MUST stay as the first actual Streamlit command
st.set_page_config(page_title="Electronics Expert AI", page_icon="⚡", layout="centered")

# --- 3. API Key Bridge ---
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if api_key:
    os.environ["GROQ_API_KEY"] = api_key
else:
    st.error("🔑 GROQ_API_KEY not found! Please add it to Streamlit Secrets.")
    st.stop()

# --- 4. Initialize Agent in Session State ---
if "agent" not in st.session_state:
    try:
        st.session_state.agent = create_agent(
            model="groq:llama-3.3-70b-versatile",
            tools=[search_tool, wiki_tool, save_tool],
            system_prompt=(
                "You are a Senior Electronics Engineer. Use your tools to provide technical verification, "
                "component pinouts, and circuit analysis. Always cite your data when possible."
            )
        )
    except Exception as e:
        st.error(f"⚠️ Failed to connect to AI Brain: {e}")
        st.stop()

# --- 5. User Interface ---
st.title("🔬 Electronics Engineering Agent")
st.markdown("Analyze circuits, check pinouts, and verify components in real-time.")
st.divider()

# Setup Chat History
history = StreamlitChatMessageHistory(key="chat_messages")

# Display conversation history
for msg in history.messages:
    with st.chat_message(msg.type):
        st.write(msg.content)

# --- 6. User Input & Execution Logic ---
if prompt := st.chat_input("Ask about circuits, components, or datasheets..."):
    
    # Show user message immediately
    st.chat_message("user").write(prompt)

    # Process AI response
    with st.chat_message("assistant"):
        try:
            with st.status("Engineer is thinking...", expanded=True) as status:
                
                # Critical: Helps Streamlit manage background threads used by agent tools
                add_script_run_context() 

                # The 'invoke' call to the agent
                result = st.session_state.agent.invoke(
                    {"messages": history.messages + [("user", prompt)]}
                )
                
                # Extract the last message content
                full_response = result["messages"][-1].content
                
                # Update history manually
                history.add_user_message(prompt)
                history.add_ai_message(full_response)
                
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            # Display final answer
            st.write(full_response)
            
        except Exception as e:
            st.error("🚨 An error occurred during analysis:")
            st.exception(e)