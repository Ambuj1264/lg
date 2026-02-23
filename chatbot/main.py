from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END, add_messages
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")

# define the state
class ChatState(TypedDict):
    # Using 'messages' (plural) is conventional for add_messages reducer
    messages: Annotated[list[BaseMessage], add_messages]


# checkpointer
checkpointer = MemorySaver()

# define the graph 
graph = StateGraph(ChatState)

# define the chat node 
def chat_node(state: ChatState):
    # Pass the list of messages directly to the model
    response = model.invoke(state["messages"])
    return {"messages": [response]}

graph.add_node("chat_node", chat_node)

# add the edges to the graph 
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# compile the graph 
app = graph.compile(checkpointer=checkpointer)

# execute the graph 
# Provide the initial message as a list
# workflow = app.invoke({"messages": [HumanMessage(content="i am fine what about you ?")]})

# print the result 
# print(workflow["messages"][-1].content)
thread_id = "thread_2"
while True:
    user_input = input("You: ")
    if user_input == "exit":
        break
    workflow = app.invoke({"messages": [HumanMessage(content=user_input)]}, config={"configurable": {"thread_id": thread_id}})
    print("Bot: ", workflow["messages"][-1].content)


