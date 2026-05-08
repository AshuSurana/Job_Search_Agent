from openai import OpenAI
from app.tools import search_jobs, extract_skills, compare_skills, extract_resume_skills
from app.prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT, COVER_LETTER_PROMPT
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
            "description": "Use AI to extract technical skills (Python, React, SQL, etc.) from job description",
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
def execute_tool(name, args, state):
    global jobs_fetched, job_skills_extracted

    if name == "search_jobs":
        if jobs_fetched:
            print(" Skipping duplicate search_jobs")
            return "Jobs already fetched"

        jobs_fetched = True
        return search_jobs(args.get("query", ""))

    elif name == "extract_skills":
        if job_skills_extracted:
            print(" Skipping duplicate extract_skills")
            return "Already extracted"

        job_skills_extracted = True
        return extract_skills(args.get("job_description", "")[:1000])

    elif name == "extract_resume_skills":
        return extract_resume_skills(args.get("resume_text", ""))

    elif name == "compare_skills":
        #  Use STATE instead of LLM args (important)
        return compare_skills(
            state.get("resume_skills", ""),
            state.get("job_skills", "")
        )

    return "Unknown tool"


# MAIN AGENT LOOP
def run_agent(user_input, resume_text=None):
    global jobs_fetched, job_skills_extracted

    # Reset flags
    jobs_fetched = False
    job_skills_extracted = False

    # State memory
    state = {
        "job": None,
        "job_skills": None,
        "resume_skills": None
    }

    job_data = []

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    if resume_text:
        messages.append({
            "role": "system",
            "content": f"User Resume:\n{resume_text}"
        })

    for step in range(7):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)

            for call in msg.tool_calls:
                tool_name = call.function.name

                try:
                    args = json.loads(call.function.arguments)
                except:
                    args = {}

                result = execute_tool(tool_name, args, state)  # ← pass state

                # Save to state
                if tool_name == "search_jobs":
                    state["job"] = result
                    try:
                        job_data = json.loads(result)
                    except:
                        job_data = []
                elif tool_name == "extract_skills":
                    state["job_skills"] = result
                elif tool_name == "extract_resume_skills":
                    state["resume_skills"] = result

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result
                })

        else:
            return msg.content, job_data

    return "Agent stopped", job_data

def run_selected_job_analysis(selected_job, resume_text):
    title = str(selected_job.get("title", "Unknown Role"))
    company = str(selected_job.get("company", "Unknown Company"))
    description = str(selected_job.get("description", "")).strip()

    if not description:
        return "Could not analyze because selected job description is empty.", {}

    job_skills = extract_skills(description[:2000])
    resume_skills = extract_resume_skills(resume_text or "")
    comparison = compare_skills(resume_skills, job_skills)

    user_payload = f"""
Selected Job:
Title: {title}
Company: {company}
Description: {description}

Resume:
{resume_text}

Extracted Job Skills:
{job_skills}

Extracted Resume Skills:
{resume_skills}

Skill Comparison:
{comparison}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": ANALYSIS_PROMPT},
            {"role": "user", "content": user_payload},
        ],
        temperature=0
    )

    final_text_full = response.choices[0].message.content
    
    # Split text from JSON (Robustly)
    if "MANDATORY UI_STATS_JSON:" in final_text_full:
        parts = final_text_full.split("MANDATORY UI_STATS_JSON:")
        final_text = parts[0].strip()
        json_str = parts[1].strip()
        
        # Remove potential markdown code blocks
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        try:
            stats = json.loads(json_str)
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            stats = {"matched_skills": [], "missing_skills": []}
    else:
        final_text = final_text_full
        stats = {"matched_skills": [], "missing_skills": []}

    return final_text, {
        "job_skills": job_skills,
        "resume_skills": resume_skills,
        "comparison": comparison,
        "stats": stats # New AI-driven stats
    }

def generate_cover_letter(job_details, resume_text, tone="Professional"):
    title = job_details.get("title", "Unknown Role")
    company = job_details.get("company", "Unknown Company")
    description = job_details.get("description", "")

    prompt = COVER_LETTER_PROMPT.format(
        title=title,
        company=company,
        description=description[:2000],
        resume=resume_text[:2000],
        tone=tone
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional career writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content