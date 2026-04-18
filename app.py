import streamlit as st
import os
from langchain.agents import create_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_groq import ChatGroq
from tools import search_tool, wiki_tool, save_tool

# --- 1. Robust 2026 Import Bridge ---
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

# --- DESIGN: Custom Background Image ---
# REPLACE THE LINK BELOW with your Raw GitHub Link
my_bg_url = "https://github.com/6sarveshr9/electronicschat69/blob/4cb5978bd3a36d8ceea7a3eb221f896d6d0c7e14/gargantua-endurance-5120x3662-25445.jpg?raw=true"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{https://github.com/6sarveshr9/electronicschat69/blob/a4fb999ede6803cdd93eaa4b6d1a37d3983c26ae/gargantua-endurance-5120x3662-25445.jpg}");
        background-attachment: fixed;
        background-size: cover;
    }}
    
    /* Dark overlay to keep text readable */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.7); 
        z-index: -1;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

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

history = StreamlitChatMessageHistory(key="chat_messages")

for msg in history.messages:
    with st.chat_message(msg.type):
        st.write(msg.content)

# --- 6. Execution Logic ---
if prompt := st.chat_input("What brings you here today?"):
    
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            with st.status("I'm working on it...", expanded=True) as status:
                add_script_run_context() 

                result = st.session_state.agent.invoke(
                    {"messages": history.messages + [("user", prompt)]}
                )
                
                full_response = result["messages"][-1].content
                status.update(label="Done!", state="complete", expanded=False)
            
            response_placeholder.write(full_response)
            history.add_user_message(prompt)
            history.add_ai_message(full_response)
            
        except Exception as e:
            error_str = str(e)
            if any(err in error_str for err in ["tool_use_failed", "400", "invalid_request_error"]):
                st.warning("⚠️ High traffic on tool-parser. Using internal knowledge...")
                
                try:
                    fallback_llm = ChatGroq(model="llama-3.3-70b-versatile")
                    fallback_resp = fallback_llm.invoke([
                        ("system", "You are a Senior Electronics Engineer. Answer precisely using internal knowledge."),
                        ("user", prompt)
                    ])
                    
                    full_response = fallback_resp.content
                    response_placeholder.write(full_response)
                    history.add_user_message(prompt)
                    history.add_ai_message(full_response)
                except Exception as fallback_err:
                    st.error(f"🚨 Critical Failure: {fallback_err}")
            else:
                st.error("🚨 Technical Error Encountered:")
                st.exception(e)