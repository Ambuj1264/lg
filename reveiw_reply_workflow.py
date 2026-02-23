from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")


class SentimentSchema(BaseModel):
    sentiment: Literal["positive", "negative"]= Field(description="Sentiment of the text")



structured_model= model.with_structured_output(SentimentSchema)


prompt = """
What is the sentiment of the following review - The software too good
"""


# result = structured_model.invoke(prompt)
# print(result)


class ReviewState(TypedDict):
    review: str
    sentiment: Literal["positive", "negative"]
    diagnosis: dict
    response: str


# define the graph 

graph = StateGraph(ReviewState)


# add the nodes to the graph 


def find_sentiment(state: ReviewState):
    prompt= f"for the following review find out the sentiment \n {state['review']}"
    result = structured_model.invoke(prompt)
    return {"sentiment": result.sentiment}


    # add condition

def check_sentiment(state: ReviewState)-> Literal["positive_response", "negative_response"]:
    if state['sentiment'] == "positive":
        return "positive_response"
    else:
        return "run_diagnosis"


def positive_response(state: ReviewState):
    prompt= f"for the following review find out the sentiment \n {state['review']}"
    result = structured_model.invoke(prompt)
    return {"response": result.sentiment}

def negative_response(state: ReviewState):
    prompt= f"for the following review find out the sentiment \n {state['review']}"
    result = structured_model.invoke(prompt)
    return {"response": result.sentiment}

def run_diagnosis(state: ReviewState):
    prompt= f"for the following review find out the sentiment \n {state['review']}"
    result = structured_model.invoke(prompt)
    return {"response": result.sentiment}


graph.add_node("find_sentiment", find_sentiment)
graph.add_node("positive_response", positive_response)
graph.add_node("negative_response", negative_response)
graph.add_node("run_diagnosis", run_diagnosis)




# add the edges to the graph 

graph.add_edge(START, "find_sentiment")
graph.add_conditional_edges(
    "find_sentiment",
    check_sentiment,
    {
        "positive_response": "positive_response",
        "run_diagnosis": "run_diagnosis"
    }
)
graph.add_edge("positive_response", END)
graph.add_edge("negative_response", END)
graph.add_edge("run_diagnosis", END)


# compile the graph 
app = graph.compile()

# execute the graph 
workflow = app.invoke({"review": "The software too bad"})

# print the result 
print(workflow)







