import streamlit as st
import os
from langchain.agents import create_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_groq import ChatGroq
from tools import search_tool, wiki_tool, save_tool

# --- 1. Robust 2026 Import Bridge ---
try:
    from streamlit.runtime.scriptrunner_utils.script_run_context import add_script_run_context
except ImportError:
    try:
        from streamlit.runtime.scriptrunner.script_run_context import add_script_run_context
    except ImportError:
        try:
            from streamlit.runtime.scriptrunner import add_script_run_context
        except ImportError:
            def add_script_run_context(thread=None):
                return None

# --- 2. Page Configuration ---
st.set_page_config(page_title="Electronics Expert AI", page_icon="⚡", layout="centered")

# --- 3. API Key Bridge ---
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if api_key:
    os.environ["GROQ_API_KEY"] = api_key
else:
    st.error("🔑 GROQ_API_KEY not found! Please add it to Streamlit Secrets.")
    st.stop()

# --- 4. Initialize Agent ---
if "agent" not in st.session_state:
    try:
        st.session_state.agent = create_agent(
            model="groq:llama-3.3-70b-versatile",
            tools=[search_tool, wiki_tool, save_tool],
            system_prompt=(
                "You are a Senior Electronics Engineer. Use search_tool for specific component data. "
                "Provide pinouts in tables and circuit advice in clear steps."
            )
        )
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        st.stop()

# --- 5. UI Elements ---
st.title("🔬 Electronics Engineering Agent")
st.markdown("Analyze circuits and components with real-time web verification.")
st.divider()

history = StreamlitChatMessageHistory(key="chat_messages")

for msg in history.messages:
    with st.chat_message(msg.type):
        st.write(msg.content)

# --- 6. Execution Logic ---
if prompt := st.chat_input("Ask about a component (e.g., 'Pinout of NE555 timer')"):
    
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            with st.status("Engineer is analyzing...", expanded=True) as status:
                add_script_run_context() 

                result = st.session_state.agent.invoke(
                    {"messages": history.messages + [("user", prompt)]}
                )
                
                full_response = result["messages"][-1].content
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            st.write(full_response)
            history.add_user_message(prompt)
            history.add_ai_message(full_response)
            
        except Exception as e:
            # Check for the specific tool formatting/BadRequest error
            if "tool_use_failed" in str(e) or "400" in str(e):
                st.warning("⚠️ Tool-parser glitch. Switching to internal knowledge fallback...")
                
                # Directly call the LLM to bypass the failing tool-logic
                fallback_llm = ChatGroq(model="groq:llama-3.3-70b-versatile")
                fallback_resp = fallback_llm.invoke([
                    ("system", "You are a Senior Electronics Engineer. Answer the user's question precisely using your internal knowledge."),
                    ("user", prompt)
                ])
                
                final_text = fallback_resp.content
                st.write(final_text)
                history.add_user_message(prompt)
                history.add_ai_message(final_text)
            else:
                st.error("🚨 Technical Error:")
                st.exception(e)