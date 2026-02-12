from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv



load_dotenv()


# define the model with openai 
model = ChatOpenAI(model="gpt-4o-mini")



# define the state 

class LLMState(TypedDict):
    question:str
    answer:str


#  define the graph 

graph = StateGraph(LLMState)


#  add the node to your graph

def ask_llm(state: LLMState):
    # extract the question from the state
    question = state["question"]
    # form a model prompt 
    prompt = f"""You are a helpful assistant. Answer the following question: {question}"""
    answer = model.invoke(prompt)

    # extract the answer from the model response
    state["answer"] = answer.content
    return state

graph.add_node("ask_llm", ask_llm)


#  add the edges to your graph 
graph.add_edge(START, "ask_llm")
graph.add_edge("ask_llm", END)


#  compile your graph 
app = graph.compile()


#  execute your graph 
workflow = app.invoke({"question": "What is the capital of France?"})


#  print the result 
print(workflow)

# print the graph
print(app.get_graph().draw_ascii())


