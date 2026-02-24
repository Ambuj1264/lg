from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


# define the model with openai
model = ChatOpenAI(model="gpt-4o-mini")


# define the state

class JokeState(TypedDict):
    joke: str
    topic: str
    explanation: str


# graph definition

graph = StateGraph(JokeState)



# nodes definition
def generate_joke(state: JokeState):
    prompt = f"Generate a joke about {state['topic']}"
    joke = model.invoke(prompt)
    return {"joke": joke.content}


def explain_joke(state: JokeState):
    prompt = f"Explain the following joke: {state['joke']}"
    explanation = model.invoke(prompt)
    return {"explanation": explanation.content}

graph.add_node("generate_joke", generate_joke)
graph.add_node("explain_joke", explain_joke)

# edges definition
graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "explain_joke")
graph.add_edge("explain_joke", END)

# checkpointing with memory
checkpoint = InMemorySaver()

# execute or compile 
app = graph.compile(checkpointer=checkpoint)
workflow = app.invoke({"topic": "programming"}, config={"configurable": {"thread_id": "thread-1"}})

print(workflow)
 

print(list(app.get_state_history({"configurable": {"thread_id": "thread-1"}})))