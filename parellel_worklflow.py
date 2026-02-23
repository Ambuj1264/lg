from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")

class BatsmanState(TypedDict, total=False):
    name: str
    runs: int
    fours: int
    sixes: int
    innings: int
    sr: float
    bpb: float
    boundary_percentage: float
    summary: str

graph = StateGraph(BatsmanState)

# --- parallel nodes: return ONLY the update ---
def calculate_sr(state: BatsmanState):
    return {"sr": state["runs"] / state["innings"]}

def calculate_bpb(state: BatsmanState):
    return {"bpb": (state["fours"] + state["sixes"]) / state["innings"]}

def calculate_boundary_percentage(state: BatsmanState):
    # NOTE: your formula is same as bpb; if you meant boundary runs %, adjust it.
    return {"boundary_percentage": (state["fours"] + state["sixes"]) / state["innings"]}

def summary(state: BatsmanState):
    # Guard: don't run until all metrics exist, and don't run twice
    if "summary" in state:
        return {}
    if not all(k in state for k in ("sr", "bpb", "boundary_percentage")):
        return {}

    prompt = (
        f"Summarize the following batsman performance:\n"
        f"Name: {state['name']}\n"
        f"Runs: {state['runs']}\n"
        f"Fours: {state['fours']}\n"
        f"Sixes: {state['sixes']}\n"
        f"Innings: {state['innings']}\n"
        f"SR: {state['sr']:.2f}, BPB: {state['bpb']:.2f}, Boundary%: {state['boundary_percentage']:.2f}"
    )
    return {"summary": model.invoke(prompt).content}

graph.add_node("calculate_sr", calculate_sr)
graph.add_node("calculate_bpb", calculate_bpb)
graph.add_node("calculate_boundary_percentage", calculate_boundary_percentage)
graph.add_node("summary", summary)

# fan-out in parallel
graph.add_edge(START, "calculate_sr")
graph.add_edge(START, "calculate_bpb")
graph.add_edge(START, "calculate_boundary_percentage")

# each calc tries to trigger summary; guard ensures only final one writes it
graph.add_edge("calculate_sr", "summary")
graph.add_edge("calculate_bpb", "summary")
graph.add_edge("calculate_boundary_percentage", "summary")

graph.add_edge("summary", END)

app = graph.compile()

workflow = app.invoke({"name": "Virat Kohli", "runs": 100, "fours": 10, "sixes": 5, "innings": 50})
print(workflow) 
