from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from all import SearchState
from search_query import understand_query_node
from api import tavily_search_node
from answer import generate_answer_node


def create_search_assistant():
    workflow = StateGraph(SearchState)

    workflow.add_node("understand", understand_query_node)
    workflow.add_node("search", tavily_search_node)
    workflow.add_node("answer", generate_answer_node)

    workflow.add_edge(START, "understand")
    workflow.add_edge("understand", "search")
    workflow.add_edge("search", "answer")
    workflow.add_edge("answer", END)

    memory = InMemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app