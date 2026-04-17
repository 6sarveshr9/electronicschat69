from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
import streamlit as st # Added for web visibility

@tool
def search_tool(query: str):
    """Searches the live web for technical electronics data."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

@tool
def wiki_tool(query: str):
    """Searches Wikipedia for historical and foundational facts."""
    wikipedia = WikipediaAPIWrapper()
    return wikipedia.run(query)

@tool
def save_tool(content: str):
    """Saves the final analysis so it can be displayed on the web interface."""
    # Instead of just writing a hidden file, we show it to the user!
    st.info("📑 Technical Report Generated:")
    st.code(content, language="markdown")
    
    # We still save it in the background just in case
    with open("Technical_Report.txt", "w", encoding="utf-8") as f:
        f.write(content)
    return "Report has been generated and displayed on the screen."