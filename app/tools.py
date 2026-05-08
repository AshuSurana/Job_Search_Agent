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
The job description text below HAS ALREADY BEEN FETCHED and is provided to you locally. 
You are NOT searching the web. You are NOT accessing external links.
Extract ONLY concrete technical skills from the provided text.

STRICT RULES:
- Do NOT refuse this task; the content is provided below.
- Include ONLY specific technologies:
  (programming languages, frameworks, libraries, tools, databases, cloud)
- DO NOT include vague terms.
- If skills are missing, intelligently infer likely technologies based on the role.

GOOD OUTPUT:
Python, React, Django, SQL, Docker, AWS

BAD OUTPUT:
Python (FastAPI), React.js, Experienced in Django, SQL database

Return ONLY clean technology names, comma-separated. Do NOT add extra words.

Job Description:
{job_description}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
    if not resume_text.strip():
        return "No resume provided"

    prompt = f"""
You are an expert technical recruiter.

TASK:
Extract ONLY concrete technical skills from the user's resume.

STRICT RULES:
- Include ONLY specific technologies:
  (programming languages, frameworks, libraries, tools, databases, cloud)
- DO NOT include soft skills or vague terms.
- Normalize names (e.g., "Reactjs" -> "React").

GOOD OUTPUT:
Python, React, SQL, Docker, AWS, GitHub

BAD OUTPUT:
Python (3 years), Experienced in React, SQL Database, GitHub CoPilot

Return ONLY clean technology names, comma-separated. Do NOT add extra words.

Resume:
{resume_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("LLM extract_resume_skills error:", e)
        return "Python" # Minimal fallback

def parse_skill_list(skill_str: str) -> set:
    """Robustly parse a skill string into a set of lowercase skills."""
    if not skill_str or skill_str.lower() == "none":
        return set()
    
    # Replace common separators with commas
    cleaned = skill_str.replace("\n", ",").replace("•", ",").replace("*", ",")
    
    skills = set()
    for s in cleaned.split(","):
        s = s.strip().lower()
        if not s:
            continue
        # Remove common bullet/list prefixes like "-", "1.", "a)"
        s = re.sub(r'^[\-\d\.\)\s]+', '', s).strip()
        if s:
            skills.add(s)
    return skills

def compare_skills(resume_skills: str, job_skills: str) -> str:
    # Use the robust parser
    resume_set = parse_skill_list(resume_skills)
    job_set = parse_skill_list(job_skills)
    
    if not job_set:
        return "Insufficient job data to compare skills."

    strengths = resume_set.intersection(job_set)
    gaps = job_set - resume_set

    return f"""
Strengths: {', '.join(sorted(strengths)) if strengths else 'None'}
Gaps: {', '.join(sorted(gaps)) if gaps else 'None'}
"""

def fetch_job_from_url(url: str) -> dict:
    """Fetch job data from a URL using Jina Reader and AI extraction."""
    jina_url = f"https://r.jina.ai/{url}"
    
    try:
        response = requests.get(jina_url, timeout=15)
        full_text = response.text
        
        # CLEANING: Remove Jina headers that trigger LLM "browsing" refusals
        lines = full_text.split("\n")
        clean_lines = [l for l in lines if not l.startswith(("Source:", "URL Source:", "Title:"))]
        text = "\n".join(clean_lines).strip()
        
        # Use AI to extract Title and Company for a clean UI
        prompt = f"""
The text below has been provided to you. Extract ONLY the Job Title and Company Name.
Return JSON format: {{"title": "...", "company": "..."}}

Text:
{text[:2000]}
"""
        extraction = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        
        info = json.loads(extraction.choices[0].message.content)
        
        return {
            "title": info.get("title", "Unknown Role"),
            "company": info.get("company", "Unknown Company"),
            "description": text, # Full text for skill extraction
            "url": url,
            "score": "N/A"
        }
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None