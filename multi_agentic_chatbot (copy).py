# ------------------ Imports ------------------
from typing import Annotated
from typing_extensions import TypedDict

# LangGraph & Tools
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# LangChain Tools
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun

# LLM (Groq)
from langchain_groq import ChatGroq

from IPython.display import Image, display
from PyQt5.QtGui import QKeyEvent
# ------------------ Tool Setup ------------------
arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=300)
arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_wrapper)

wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=300)
wiki_tool = WikipediaQueryRun(api_wrapper=wiki_wrapper)

tools = [wiki_tool, arxiv_tool]

# ------------------ LangGraph State ------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]

# ------------------ LLM Setup ------------------
groq_api_key = "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"
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Gemma2-9b-It")
llm_with_tools = llm.bind_tools(tools=tools)

# ------------------ Node Function ------------------
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# ------------------ Build the Graph ------------------
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

# ------------------ Visualize Graph ------------------
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    print("Mermaid visualization requires additional dependencies.")

# ------------------ Memory & Tool Tracking ------------------
memory = []
tool_usage_log = []

# ------------------ Chat Simulation ------------------
def run_chatbot(user_input: str) -> str:
    memory.append(("user", user_input))
    tool_info = {
        "user_input": user_input,
        "tool_used": None,
        "tool_input": None,
        "tool_output": None,
        "ai_response": None,  # <-- NEW
    }

    events = graph.stream({"messages": memory}, stream_mode="values")

    pending_tool_name = None
    pending_tool_args = None
    final_ai_response = None

    for event in events:
        latest = event["messages"][-1]
        latest.pretty_print()

        if latest.type == "ai":
            final_ai_response = latest.content

            if getattr(latest, "tool_call", None):
                pending_tool_name = latest.tool_call["name"]
                pending_tool_args = latest.tool_call["args"]

        elif latest.type == "tool":
            tool_info["tool_used"] = pending_tool_name
            tool_info["tool_input"] = pending_tool_args
            tool_info["tool_output"] = latest.content
            pending_tool_name = None
            pending_tool_args = None

        memory.append(("ai", latest.content))

    tool_info["ai_response"] = final_ai_response
    tool_usage_log.append(tool_info)
    Response = final_ai_response
    return final_ai_response  # <-- RETURN the AI message



# ------------------ Example Query ------------------
if __name__ == '__main__':
    run_chatbot("who is bilgates")  # ✅ OK IF you don't import this module

    # ------------------ Print Tool Log ------------------

    print("\n--- Tool Usage Log ---")
    for entry in tool_usage_log:
        print(f"\nUser Asked     : {entry['user_input']}")
        print(f"Tool Used      : {entry['tool_used']}")
        print(f"Tool Input     : {entry['tool_input']}")
        print(f"Tool Output    : {entry['tool_output']}")
