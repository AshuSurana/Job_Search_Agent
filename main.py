from app.agent import run_agent

with open("data/resume.txt") as f:
    resume = f.read()

if __name__ == "__main__":
    user_input = input("What do you want? ")
    run_agent(user_input, resume)