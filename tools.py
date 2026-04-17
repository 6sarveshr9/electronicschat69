from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
import streamlit as st

@tool
def search_tool(query: str):
    """
    Search the live web for technical electronics data, datasheets, and pinouts.
    Input MUST be a simple search query string. DO NOT pass JSON or dictionaries.
    """
    # Force the query to be a plain string to prevent 400 Bad Request errors
    clean_query = str(query).strip("{}'\" ")
    
    try:
        search = DuckDuckGoSearchRun()
        return search.run(clean_query)
    except Exception as e:
        return f"Search failed. Please try rephrasing the component name. Error: {e}"

@tool
def wiki_tool(query: str):
    """
    Search Wikipedia for foundational electronics concepts, history, or component definitions.
    Input MUST be a simple search term or phrase.
    """
    clean_query = str(query).strip("{}'\" ")
    
    wikipedia = WikipediaAPIWrapper()
    try:
        return wikipedia.run(clean_query)
    except Exception:
        return f"No Wikipedia results found for '{clean_query}'. Try using search_tool instead."

@tool
def save_tool(content: str):
    """
    Generates a technical report and displays it on the user interface. 
    Use this when a final summary or datasheet analysis is ready.
    Input is the full text content of the report.
    """
    st.info("📑 Technical Report Generated:")
    st.code(content, language="markdown")
    
    try:
        with open("Technical_Report.txt", "w", encoding="utf-8") as f:
            f.write(content)
        return "The report has been successfully displayed and saved."
    except Exception as e:
        return f"Report displayed on screen, but local file save failed: {e}"