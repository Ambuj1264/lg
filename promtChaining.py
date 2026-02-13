from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")


class BlogState(TypedDict):
    title: str
    content: str
    outline: str


graph = StateGraph(BlogState)


def create_outline(state: BlogState) -> BlogState:
    prompt = f"Create an outline for the following blog post: {state['content']}"
    state["outline"] = model.invoke(prompt).content
    return state

def create_blog(state: BlogState) -> BlogState:
    prompt = f"Create a blog post based on the following outline: {state['outline']}"
    state["content"] = model.invoke(prompt).content
    return state


# node creating 


graph.add_node("create_outline", create_outline)
graph.add_node("create_blog", create_blog)


#  extending the graph 

graph.add_edge(START, "create_outline")
graph.add_edge("create_outline", "create_blog")
graph.add_edge("create_blog", END)

app = graph.compile()

workflow = app.invoke({"title": "My First Blog Post", "content": "This is my first blog post."})

print(workflow)




