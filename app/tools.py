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
            description = clean_html(job["description"]).lower()
            text = title + " " + description

            score = 0

            # 1. HARD FILTERS (strict reject)
            
            # Must include Python
            if "python" not in text:
                continue

            # Remove unwanted roles
            if any(x in title for x in ["trader", "sales", "marketing"]):
                continue

            # Remove senior roles
            if any(x in title for x in ["senior", "lead", "architect", "principal"]):
                continue

            # 2. BASE SCORING (query match)
            
            for word in query_words:
                if word in text:
                    score += 1

            # 3. ROLE ALIGNMENT (important)
           
            if any(x in title for x in [
                "engineer",
                "developer",
                "ai",
                "ml",
                "fullstack",
                "full stack",
                "backend"
            ]):
                score += 3

            # Extra boost for fullstack
            if "fullstack" in title or "full stack" in title:
                score += 3

            # 4. SKILL BOOST (your profile)
           
            # AI boost
            if any(x in text for x in ["ai", "machine learning", "ml", "llm"]):
                score += 3

            # Fullstack boost
            if any(x in text for x in ["react", "django", "flask", "javascript"]):
                score += 2

            # 5. PENALTIES (soft filtering)
           
            if any(x in title for x in ["data engineer", "databricks", "etl"]):
                if not any(x in title for x in ["developer", "engineer"]):
                    score -= 2

            # FINAL SELECTION
           
            if score >= 4:
                results.append({
                    "title": job["title"],
                    "description": description[:300],
                    "score": score
                })

        if not results:
            return "No relevant Python AI / Fullstack jobs found."

        results = sorted(results, key=lambda x: x["score"], reverse=True)

        return str(results[0])

    except Exception as e:
        return f"Error: {str(e)}"


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