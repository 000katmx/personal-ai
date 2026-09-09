from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from typing import TypedDict, Literal, List, Any
from agent_tools import web_search, get_system_info

class AgentState(TypedDict):
    messages: List[Any]
    next_step: Literal["web_search", "system_info", "chat", "end"]

# Ollama local model setup (Completely free, zero API key needed)
llm = ChatOllama(
    model="llama3",
    temperature=0.3
)

def classify_intent(state: AgentState):
    """Determine if user wants web search, system info, or general chat."""
    messages = state["messages"]
    last_msg_obj = messages[-1]
    
    # Safely extract text content regardless of object type or dict
    if hasattr(last_msg_obj, "content"):
        last_msg = last_msg_obj.content.lower()
    elif isinstance(last_msg_obj, dict):
        last_msg = last_msg_obj.get("content", "").lower()
    else:
        last_msg = str(last_msg_obj).lower()
    
    if any(word in last_msg for word in ["search", "google", "duckduckgo", "find", "look up", "news", "latest"]):
        return {"next_step": "web_search"}
    elif any(word in last_msg for word in ["system", "cpu", "memory", "network", "info", "diagnostic", "hostname"]):
        return {"next_step": "system_info"}
    else:
        return {"next_step": "chat"}

def execute_tool(state: AgentState):
    """Run the selected tool or chat directly via Ollama."""
    step = state["next_step"]
    last_msg_obj = state["messages"][-1]
    
    if hasattr(last_msg_obj, "content"):
        last_query = last_msg_obj.content
    elif isinstance(last_msg_obj, dict):
        last_query = last_msg_obj.get("content", "")
    else:
        last_query = str(last_msg_obj)
    
    if step == "web_search":
        result = web_search.invoke({"query": last_query})
    elif step == "system_info":
        result = get_system_info.invoke({})
    else:
        response = llm.invoke([
            SystemMessage(content="You are a helpful AI assistant."), 
            HumanMessage(content=last_query)
        ])
        result = response.content
    
    state["messages"].append({"role": "assistant", "content": result})
    return {"messages": state["messages"], "next_step": "end"}

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("classify", classify_intent)
workflow.add_node("execute", execute_tool)

workflow.set_entry_point("classify")
workflow.add_edge("classify", "execute")
workflow.add_edge("execute", END)

agent = workflow.compile()