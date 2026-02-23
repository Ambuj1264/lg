from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")



class QuadState(TypedDict):
    a:int
    b:int
    c:int
    equation:str
    discriminant:float
    result:str


def show_equation(state: QuadState):
    return {"equation": f"{state['a']}x^2 + {state['b']}x + {state['c']} = 0"}

def calculate_discriminant(state: QuadState):
    return {"discriminant": state['b']**2 - 4*state['a']*state['c']}

def calculate_result(state: QuadState):
    if state['discriminant'] < 0:
        return {"result": "No real roots"}
    elif state['discriminant'] == 0:
        return {"result": f"One real root: {(-state['b'] + state['discriminant']**0.5) / (2*state['a'])}"}
    else:
        return {"result": f"Two real roots: {(-state['b'] + state['discriminant']**0.5) / (2*state['a'])} and {(-state['b'] - state['discriminant']**0.5) / (2*state['a'])}"}

def real_roots(state: QuadState):
    if state['discriminant'] < 0:
        return {"result": "No real roots"}
    elif state['discriminant'] == 0:
        return {"result": f"One real root: {(-state['b'] + state['discriminant']**0.5) / (2*state['a'])}"}
    else:
        return {"result": f"Two real roots: {(-state['b'] + state['discriminant']**0.5) / (2*state['a'])} and {(-state['b'] - state['discriminant']**0.5) / (2*state['a'])}"}

def repeated_roots(state: QuadState):
    if state['discriminant'] == 0:
        return {"result": f"One real root: {(-state['b'] + state['discriminant']**0.5) / (2*state['a'])}"}
    else:
        return {"result": "No real roots"}

def no_real_roots(state: QuadState):
    if state['discriminant'] < 0:
        return {"result": "No real roots"}
    else:
        return {"result": f"Two real roots: {(-state['b'] + state['discriminant']**0.5) / (2*state['a'])} and {(-state['b'] - state['discriminant']**0.5) / (2*state['a'])}"}



#
def check_condition(state: QuadState):
    if state['discriminant'] < 0:
        return "no_real_roots"
    elif state['discriminant'] == 0:
        return "repeated_roots"
    else:
        return "real_roots"


# define the graph 
graph = StateGraph(QuadState)

# add the node to your graph 

graph.add_node("show_equation", show_equation)
graph.add_node("calculate_discriminant", calculate_discriminant)
graph.add_node("real_roots", real_roots)
graph.add_node("repeated_roots", repeated_roots)
graph.add_node("no_real_roots", no_real_roots)



# add the edges to your graph 
graph.add_edge(START, "show_equation")
graph.add_edge("show_equation", "calculate_discriminant")
graph.add_conditional_edges(
    "calculate_discriminant", 
    check_condition,
    {
        "no_real_roots": "no_real_roots",
        "repeated_roots": "repeated_roots",
        "real_roots": "real_roots"
    }
)
graph.add_edge("real_roots", END)
graph.add_edge("repeated_roots", END)
graph.add_edge("no_real_roots", END)


# compile the graph 
app = graph.compile()

# execute the graph 
workflow = app.invoke({"a": 1, "b": 2, "c": 1})

# print the result 
print(workflow)





