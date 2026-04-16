# tools.py
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper

@tool
def search_tool(query: str):
    """Searches the live web for technical electronics data."""
    # This specifically looks for the 'ddgs' package you just installed
    search = DuckDuckGoSearchRun()
    return search.run(query)

@tool
def wiki_tool(query: str):
    """Searches Wikipedia for historical and foundational facts."""
    wikipedia = WikipediaAPIWrapper()
    return wikipedia.run(query)

@tool
def save_tool(content: str, filename: str = "Technical_Report.txt"):
    """Saves the final analysis to a text file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Report saved to {filename}"