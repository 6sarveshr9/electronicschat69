from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
import streamlit as st

@tool
def search_tool(query: str):
    """
    Search the live web for technical electronics data, datasheets, and pinouts.
    Input should be a simple search query string.
    """
    search = DuckDuckGoSearchRun()
    return search.run(query)

@tool
def wiki_tool(query: str):
    """
    Search Wikipedia for foundational electronics concepts, history, or component definitions.
    Input must be a simple search term or phrase.
    """
    wikipedia = WikipediaAPIWrapper()
    try:
        return wikipedia.run(query)
    except Exception:
        return f"No Wikipedia results found for '{query}'. Try the search_tool instead."

@tool
def save_tool(content: str):
    """
    Generates a technical report and displays it on the user interface. 
    Use this when a final summary or datasheet analysis is ready.
    Input is the full text content of the report.
    """
    st.info("📑 Technical Report Generated:")
    st.code(content, language="markdown")
    
    # Save to local server storage
    with open("Technical_Report.txt", "w", encoding="utf-8") as f:
        f.write(content)
    return "The report has been successfully displayed and saved."