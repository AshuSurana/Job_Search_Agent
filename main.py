from app.agent import run_agent

with open("data/resume.txt") as f:
    resume = f.read()

if __name__ == "__main__":
    user_input = input("What do you want? ")

    print("\nPaste your resume (press Enter twice to finish):\n")

    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    resume_text = "\n".join(lines)

    run_agent(user_input, resume_text)