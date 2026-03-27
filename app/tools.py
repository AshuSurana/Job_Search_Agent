from email.mime import text
import json

import requests
import re
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=api_key
     
)
SKILLS = [
    # Languages
    "Python", "JavaScript", "C", "C++",

    # Backend
    "Django", "Flask", "FastAPI", "Node.js",

    # Frontend
    "React", "Next.js", "HTML", "CSS", "Tailwind", "Bootstrap", "Chart.js",

    # Databases
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Firebase", "Prisma",

    # DevOps / Cloud
    "Docker", "Azure",

    # AI / ML
    "Machine Learning", "Deep Learning", "LLM",
    "TensorFlow", "PyTorch", "NLP",

    # Tools
    "Git", "GitHub", "Jira", "Asana",

    # APIs / Platforms
    "OpenAI", "Gemini"
]
ALIASES = {
    "github": "Git",
    "react.js": "React",
    "node": "Node.js",
    "html5": "HTML",
    "css3": "CSS"
}

def clean_html(raw_html):
    clean = re.sub('<.*?>', '', raw_html)
    return clean

def search_jobs(query: str) -> str:
    url = "https://remotive.com/api/remote-jobs"

    try:
        response = requests.get(url)
        data = response.json()

        jobs = data.get("jobs", [])
        results = []

        query_words = query.lower().split()

        for job in jobs:
            title = job["title"].lower()
            company = job.get("company_name", "Unknown")
            description = clean_html(job["description"]).lower()
            text = title + " " + description

            score = 0

            # 1. QUERY MATCH
            
            for word in query_words:
                if word in text:
                    score += 2

            # 2. ROLE ALIGNMENT
           
            if any(x in title for x in [
                "engineer", "developer", "ai", "ml",
                "fullstack", "full stack", "backend"
            ]):
                score += 3

            # 3. SKILL BOOST
           
            if any(x in text for x in ["python", "django", "flask"]):
                score += 2

            if any(x in text for x in ["react", "javascript"]):
                score += 2

            if any(x in text for x in ["machine learning", "ai", "llm"]):
                score += 2

            # 4. SOFT PENALTIES (NOT REMOVE)
            
            if any(x in title for x in ["trader", "sales", "marketing"]):
                score -= 2

            if any(x in title for x in ["senior", "lead", "architect"]):
                score -= 1

            # 5. ALWAYS ADD (NO HARD FILTER)
            
            results.append({
                "title": job["title"],
                "company": company,
                "url": job.get("url", ""),
                "description": description[:250],
                "score": score
            })

        # SORT & RETURN TOP 3
        
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        print(f"Total jobs processed: {len(results)}")  # debug

        return json.dumps(results[:3])

    except Exception as e:
        return f"Error: {str(e)}"


def get_jobs_only(query):
    import json
    from app.tools import search_jobs

    result = search_jobs(query)

    try:
        return json.loads(result)
    except:
        return []
    
def analyze_resume(resume_text: str) -> str:
    strengths = []
    weaknesses = []

    for skill in SKILLS:
        if skill.lower() in resume_text.lower():
            strengths.append(skill)
        else:
            weaknesses.append(skill)

    return f"Strengths: {', '.join(strengths)} | Weaknesses: {', '.join(weaknesses)}"


def extract_skills(job_description: str) -> str:
    prompt = f"""
You are an expert technical recruiter.

TASK:
Extract ONLY concrete technical skills from the job description.

STRICT RULES:
- Include ONLY specific technologies:
  (programming languages, frameworks, libraries, tools, databases, cloud)
- DO NOT include vague terms like:
  "full-stack development", "scalable systems", "product development"
- If skills are missing, intelligently infer likely technologies

GOOD OUTPUT:
Python, React, Django, SQL, Docker

BAD OUTPUT:
full-stack development, clean code, scalable systems

Return ONLY comma-separated skills.

Job Description:
{job_description}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        skills = response.choices[0].message.content.strip()

        # fallback if too vague
        if not skills or any(
            vague in skills.lower()
            for vague in ["full-stack", "scalable", "development", "product"]
        ):
            return "Python, React, Django, SQL"

        return skills

    except Exception as e:
        print("LLM extract_skills error:", e)
        return "Python, React, Django, SQL"

def extract_resume_skills(resume_text: str) -> str:
    found = []

    text = resume_text.lower()

    for skill in SKILLS:
        if skill.lower() in text:
            found.append(skill)
    
    for key, value in ALIASES.items():
        if key in text:
            found.append(value)

    if not found:
        return "Python"  # minimal fallback

    return ", ".join(set(found))

def compare_skills(resume_skills: str, job_skills: str) -> str:
    
    # HANDLE UNKNOWN CASE FIRST
    if job_skills.strip().lower() == "unknown":
        return "Insufficient job data to compare skills."

    resume_set = set([s.strip().lower() for s in resume_skills.split(",")])
    job_set = set([s.strip().lower() for s in job_skills.split(",")])

    strengths = resume_set.intersection(job_set)
    gaps = job_set - resume_set

    return f"""
Strengths: {', '.join(strengths) if strengths else 'None'}
Gaps: {', '.join(gaps) if gaps else 'None'}
"""