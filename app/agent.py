from openai import OpenAI
from app.tools import search_jobs, extract_skills, compare_skills, extract_resume_skills
from app.prompts import SYSTEM_PROMPT
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(" OPENAI_API_KEY not found. Check your .env file.")

# Initialize client
client = OpenAI(
    api_key=api_key
     
)


# TOOL DEFINITIONS (for LLM)
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": "Search for jobs based on a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Job search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "extract_skills",
            "description": "Extract key skills from a job description",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_description": {
                        "type": "string",
                        "description": "Job description text"
                    }
                },
                "required": ["job_description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_resume_skills",
            "description": "Extract skills from resume",
            "parameters": {
                "type": "object",
                "properties": {
                    "resume_text": {
                        "type": "string",
                        "description": "Full resume text"
                    }
                },
                "required": ["resume_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_skills",
            "description": "Compare resume with job skills",
            "parameters": {
                "type": "object",
                "properties": {
                    "resume_skills": {"type": "string"},
                    "job_skills": {"type": "string"}
                },
                "required": ["resume_skills", "job_skills"]
            }
        }
    }
]

# TOOL EXECUTION ROUTER
def execute_tool(name, args):
    global jobs_fetched

    if name == "search_jobs":
        if jobs_fetched:
            print("⛔ Skipping duplicate search_jobs")
            return "Jobs already fetched"

        jobs_fetched = True
        return search_jobs(args["query"])

    
    elif name == "extract_skills":
        return extract_skills(args["job_description"])
    
    elif name == "extract_resume_skills":
        return extract_resume_skills(args["resume_text"])

    elif name == "compare_skills":
        return compare_skills(
            args["resume_skills"],
            args["job_skills"]
        )
    return "Unknown tool"


# MAIN AGENT LOOP
def run_agent(user_input, resume_text=None):
    global jobs_fetched
    jobs_fetched = False
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    # Optional: inject resume into context
    if resume_text:
        messages.append({
            "role": "system",
            "content": f"User Resume:\n{resume_text}"
        })

    print("\n🚀 Starting Agent...\n")

    # Prevent infinite loops
    for step in range(7):
        print(f"\n--- AGENT STEP {step + 1} ---")

        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # low-cost model
            messages=messages,
            tools=tools
        )

        msg = response.choices[0].message

        
        # TOOL CALL HANDLING
        
        if msg.tool_calls:
            messages.append(msg)

            for call in msg.tool_calls:
                tool_name = call.function.name
                print(f"🧠 Agent decided to use: {tool_name}")
                print(f"🔧 Calling tool: {tool_name}")

                try:
                    args = json.loads(call.function.arguments)
                except Exception as e:
                    print("❌ JSON parsing error:", e)
                    args = {}

                result = execute_tool(tool_name, args)

                print(f"📤 Tool result: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result
                })

        
        # FINAL RESPONSE
        
        else:
            print("\n✅ FINAL ANSWER:\n")
            print(msg.content)
            break

    else:
        print("\n⚠️ Agent stopped (max steps reached)")