from email.mime import text
import json

import requests
import re

SKILLS = [
    # Core
    "Python", "JavaScript", "C++",

    # Backend
    "Django", "Flask", "FastAPI",

    # Frontend
    "React", "Next.js", "HTML", "CSS", "Tailwind",

    # Databases
    "SQL", "PostgreSQL", "MongoDB", "Firebase",

    # DevOps / Cloud
    "Docker", "Azure",

    # AI / ML
    "Machine Learning", "Deep Learning", "LLM",
    "TensorFlow", "PyTorch", "NLP"
]

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

            # -------------------------------
            # 1. HARD FILTERS (strict reject)
            # -------------------------------

            # Must include Python
            if "python" not in text:
                continue

            # Remove unwanted roles
            if any(x in title for x in ["trader", "sales", "marketing"]):
                continue

            # Remove senior roles
            if any(x in title for x in ["senior", "lead", "architect", "principal"]):
                continue

            # -------------------------------
            # 2. BASE SCORING (query match)
            # -------------------------------

            for word in query_words:
                if word in text:
                    score += 1

            # -------------------------------
            # 3. ROLE ALIGNMENT (important)
            # -------------------------------

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

            # -------------------------------
            # 4. SKILL BOOST (your profile)
            # -------------------------------

            # AI boost
            if any(x in text for x in ["ai", "machine learning", "ml", "llm"]):
                score += 3

            # Fullstack boost
            if any(x in text for x in ["react", "django", "flask", "javascript"]):
                score += 2

            # -------------------------------
            # 5. PENALTIES (soft filtering)
            # -------------------------------

            if any(x in title for x in ["data engineer", "databricks", "etl"]):
                if not any(x in title for x in ["developer", "engineer"]):
                    score -= 2

            # -------------------------------
            # FINAL SELECTION
            # -------------------------------

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
    SKILLS = [
        "python", "fastapi", "django", "flask",
        "react", "javascript", "docker",
        "llm", "machine learning", "deep learning",
        "tensorflow", "pytorch", "sql"
    ]

    found = []

    text = job_description.lower()

    for skill in SKILLS:
        if skill in text:
            found.append(skill)

    if not found:
        return "python, react, django"  # fallback

    return ", ".join(found)

def extract_resume_skills(resume_text: str) -> str:
    found = []

    text = resume_text.lower()

    for skill in SKILLS:
        if skill.lower() in text:
            found.append(skill)

    if not found:
        return "Python"  # minimal fallback

    return ", ".join(set(found))
def compare_skills(resume_skills: str, job_skills: str) -> str:
    resume_set = set([s.strip().lower() for s in resume_skills.split(",")])
    job_set = set([s.strip().lower() for s in job_skills.split(",")])

    strengths = resume_set.intersection(job_set)
    gaps = job_set - resume_set

    return f"""
Strengths: {', '.join(strengths) if strengths else 'None'}
Gaps: {', '.join(gaps) if gaps else 'None'}
"""