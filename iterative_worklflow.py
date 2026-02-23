
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()




from pydantic import BaseModel, Field

# Schema for evaluation
class EvaluationSchema(BaseModel):
    evaluation: Literal["approved", "need_improvement"] = Field(description="Whether the tweet is approved or needs improvement")
    feedback: str = Field(description="Feedback for improvement if needed")

generator_llm = ChatOpenAI(model="gpt-4o")
evaluator_llm = ChatOpenAI(model="gpt-3.5-turbo").with_structured_output(EvaluationSchema)
optimizer_llm = ChatOpenAI(model="gpt-4o")

# state
class TweetState(TypedDict):
    topic: str
    tweet: str
    evaluation: Literal["approved", "need_improvement"]
    feedback: str
    iteration: int
    max_iteration: int

# define the graph 
graph = StateGraph(TweetState)

# add the nodes to the graph 
def generate_tweet(state: TweetState):
    prompt = f"Generate a tweet about {state['topic']}"
    tweet = generator_llm.invoke(prompt)
    return {"tweet": tweet.content, "iteration": 1}

def evaluate_tweet(state: TweetState):
    prompt = f"Evaluate the following tweet: {state['tweet']}"
    result = evaluator_llm.invoke(prompt)
    return {"evaluation": result.evaluation, "feedback": result.feedback}

def optimize_tweet(state: TweetState):
    prompt = f"Optimize the following tweet based on feedback: {state['feedback']}\nTweet: {state['tweet']}"
    optimized_tweet = optimizer_llm.invoke(prompt)
    return {
        "tweet": optimized_tweet.content, 
        "iteration": state.get("iteration", 0) + 1
    }

graph.add_node("generate", generate_tweet)
graph.add_node("evaluate", evaluate_tweet)
graph.add_node("optimize", optimize_tweet)

# routing function
def should_continue(state: TweetState):
    if state["evaluation"] == "approved" or state["iteration"] >= state["max_iteration"]:
        return END
    return "optimize"

# add the edges to the graph 
graph.add_edge(START, "generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges("evaluate", should_continue)
graph.add_edge("optimize", "evaluate")

# compile the graph 
app = graph.compile()

# execute the graph 
workflow = app.invoke({"topic": "aasdfasdfasdf", "max_iteration": 3})

# print the result 
print(workflow)

    
    
    
