from prompts import template
from agent import run_agent

def run_pipeline(user_input: str):
    prompt = template.invoke({"user_input": user_input})
    response = run_agent(prompt)

    return response["messages"][-1].content[0]["text"]


if __name__ == "__main__":
    user_input = input("Enter your travel requirements: ")
    response = run_pipeline(user_input)
    print("\nTravel Plan:\n")
    print(response)
    
    
