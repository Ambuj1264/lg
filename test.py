from langgraph.graph import StateGraph, START, END
from typing import TypedDict



# define state

class BMIState(TypedDict):
    weight:float
    height:float
    bmi:float
    category:str



def calculate_bmi(state: BMIState):
    weight = state["weight"]
    height = state["height"]
    bmi = weight / (height * height)
    
    state["bmi"] = round(bmi, 2)
    return state

def labled_bmi(state: BMIState):
    bmi = state["bmi"]
    if bmi < 18.5:
        state["category"] = "Underweight"
    elif bmi < 25:
        state["category"] = "Normal weight"
    elif bmi < 30:
        state["category"] = "Overweight"
    else:
        state["category"] = "Obesity"
    return state

# define your graph 

graph = StateGraph(BMIState)


#  add the node to your graph 
graph.add_node("calculate_bmi", calculate_bmi)
graph.add_node("labled_bmi", labled_bmi)




# add edges to your graph 

graph.add_edge(START, "calculate_bmi")
graph.add_edge("calculate_bmi", "labled_bmi")
graph.add_edge("labled_bmi", END)



# compile your graph 

app = graph.compile()


# execute your graph 
workflow = app.invoke({"weight": 70, "height": 1.75})

#  print the result 
print(workflow)


# print(app.get_graph().draw_ascii())