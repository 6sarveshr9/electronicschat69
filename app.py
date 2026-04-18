import streamlit as st
import os
from langchain.agents import create_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_groq import ChatGroq
from tools import search_tool, wiki_tool, save_tool

# --- 1. Robust 2026 Import Bridge ---
# The '# type: ignore' tells VS Code to stop showing the "not resolved" error.
try:
    from streamlit.runtime.scriptrunner_utils.script_run_context import add_script_run_context # type: ignore
except ImportError:
    try:
        from streamlit.runtime.scriptrunner.script_run_context import add_script_run_context # type: ignore
    except ImportError:
        try:
            from streamlit.runtime.scriptrunner import add_script_run_context # type: ignore
        except ImportError:
            def add_script_run_context(thread=None):
                return None

# --- 2. Page Configuration ---
st.set_page_config(page_title="LSD Ai | Electronics Expert", page_icon="⚡", layout="centered")

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
                "You are a Senior Electronics Engineer. Use search_tool for component data. "
                "Provide pinouts in tables and circuit advice in clear steps. "
                "If tools fail, use your internal knowledge to provide engineering advice."
            )
        )
    except Exception as e:
        st.error(f"⚠️ Agent Initialization Failed: {e}")
        st.stop()

# --- 5. UI Elements ---
st.title("🔬 LSD Ai")
st.markdown("Analyze circuits and components with real-time technical verification.")
st.divider()

# Setup Chat History
history = StreamlitChatMessageHistory(key="chat_messages")

# Display conversation history
for msg in history.messages:
    with st.chat_message(msg.type):
        st.write(msg.content)

# --- 6. Execution Logic ---
if prompt := st.chat_input("What brings you here today?"):
    
    # 1. Display User Message
    st.chat_message("user").write(prompt)

    # 2. Process Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            with st.status("Working on it...", expanded=True) as status:
                # This ensures the search tool stays connected to your session
                add_script_run_context() 

                # Primary Attempt: Agent with Tools
                result = st.session_state.agent.invoke(
                    {"messages": history.messages + [("user", prompt)]}
                )
                
                full_response = result["messages"][-1].content
                status.update(label="There you go!", state="complete", expanded=False)
            
            # Success display
            response_placeholder.write(full_response)
            history.add_user_message(prompt)
            history.add_ai_message(full_response)
            
        except Exception as e:
            error_str = str(e)
            # Handle tool-parser or connection glitches
            if any(err in error_str for err in ["tool_use_failed", "400", "invalid_request_error"]):
                st.warning("⚠️ High traffic on tool-parser. Using internal knowledge...")
                
                try:
                    # Fallback directly to the LLM
                    fallback_llm = ChatGroq(model="llama-3.3-70b-versatile")
                    
                    fallback_resp = fallback_llm.invoke([
                        ("system", "You are a Senior Electronics Engineer. Answer precisely using internal knowledge."),
                        ("user", prompt)
                    ])
                    
                    full_response = fallback_resp.content
                    response_placeholder.write(full_response)
                    
                    # Update history
                    history.add_user_message(prompt)
                    history.add_ai_message(full_response)
                except Exception as fallback_err:
                    st.error(f"🚨 Critical Failure: {fallback_err}")
            else:
                st.error("🚨 Technical Error Encountered:")
                st.exception(e)