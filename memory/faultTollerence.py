from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import time
load_dotenv()

# NOTE: `ChatOpenAI` instantiation can trigger heavy imports and environment
# validation at module import time. This script doesn't use `model`, so we
# avoid creating it here to prevent import hangs.


# define the state

class CrashState(TypedDict):
    input: str
    step1: str
    step2: str
    step3: str


# define the step 
def step_1(state: CrashState)-> CrashState:
    print(" step 1 executed")
    return {"step1": "done", "input": state["input"]}

def step_2(state: CrashState)-> CrashState:
    print(" step 2 executed")
    time.sleep(30) # simulating a long running task
    return {"step2": "done"}

def step_3(state: CrashState)-> CrashState:
    print(" step 3 executed")
    return {"step3": "done"}

#  graph definition
graph = StateGraph(CrashState)


# nodes definition
graph.add_node("step_1", step_1)
graph.add_node("step_2", step_2)
graph.add_node("step_3", step_3)

# edges definition
graph.add_edge(START, "step_1")
graph.add_edge("step_1", "step_2")
graph.add_edge("step_2", "step_3")
graph.add_edge("step_3", END)

# checkpointing with memory
checkpoint = InMemorySaver()

# execute or compile
app = graph.compile(checkpointer=checkpoint)

try:
    workflow = app.invoke({"input": "start"}, config={"configurable": {"thread_id": "thread-1"}})
    print(workflow)
except Exception as e:
    print("X")


# re run to show fault tolerance resume 
final_state = app.invoke(None, config={"configurable": {"thread_id": "thread-1"}})
print(final_state)
