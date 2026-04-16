import os
from dotenv import load_dotenv
from langchain.agents import create_agent # The 2026 v1.0 Standard
from tools import search_tool, wiki_tool, save_tool 

load_dotenv()

# 1. Define the Tools
tools = [search_tool, wiki_tool, save_tool]

# 2. Create the Agent (Optimized for 2026 Groq)
# This handles the 'Think-Tool-Observe' loop automatically
agent = create_agent(
    model="groq:llama-3.3-70b-versatile",
    tools=tools,
    system_prompt="""You are a Principal Hardware Design Engineer. 
    When asked about a circuit or component:
    1. Conduct deep technical research into pinouts, voltage levels, and thermal limits.
    2. Provide DC bias points and AC frequency response characteristics.
    3. Use 'save_tool' to export a professional Engineering Verification Report (.txt)."""
)

# 3. Running the Analysis
print("--- Electronics Intelligence Agent Online ---")
user_query = input("Which circuit/component are we verifying today? ")

# Input must be a list of messages in v1.0
response = agent.invoke({"messages": [("user", user_query)]})

# 4. Display the Final Engineering Report
print("\n" + "="*50)
print("FINAL TECHNICAL ANALYSIS")
print("="*50)
print(response["messages"][-1].content)
# main.py (Modified to fix Groq 400 Error)

agent = create_agent(
    model="groq:llama-3.3-70b-versatile",
    tools=tools,
    system_prompt="""You are a Principal Hardware Design Engineer. 
    
    IMPORTANT: You must use the provided tools for research. 
    When you call a tool, use the standard tool-calling format. 
    Do NOT wrap tool calls in <function> tags or custom XML. 
    Provide only the tool name and arguments as requested by the system.

    Your goal: Provide deep technical circuit verification (pinouts, thermal limits, DC bias)."""
)