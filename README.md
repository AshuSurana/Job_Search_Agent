# Autonomous Job Search Copilot (AI Agent)

An intelligent **agentic AI system** built using Python and OpenAI SDK that automates job search, analyzes candidate skills, and identifies gaps against real-world job requirements.

---

## Overview

This project demonstrates a **multi-step autonomous agent** that:

* Searches and ranks real-time job listings using a multi-factor scoring algorithm
* Extracts required skills from job descriptions using an **LLM** (`gpt-4.1-mini`)
* Extracts skills from a candidate's resume using keyword matching + alias normalization
* Compares both skill sets to surface strengths and gaps
* Generates a final structured answer with actionable recommendations

The system uses a **tool-calling + reasoning loop with stateful memory**, simulating how modern AI agents operate.

---

##  Key Features

*  **Job Search Integration**

  * Fetches jobs from Remotive API with smart 5-layer scoring (hard filters, role alignment, skill boost, penalties, ranking)

*  **Multi-step Agent Workflow**

  * Tool-based execution with state tracking (search → extract (LLM) → resume parse → compare → final answer)
  * Deduplication guards prevent redundant tool calls

*  **Skill Extraction Engine**

  * From job descriptions — LLM-powered (`extract_skills`)
  * From resume text — keyword matching with alias normalization (`extract_resume_skills`)

*  **Skill Gap Analysis**

  * Identifies strengths vs missing skills


*  **Low-cost AI usage**

  * Uses lightweight model (`gpt-4.1-mini`)

---

##  How It Works

### Agent Workflow

1. **Search Jobs** — queries Remotive API, scores and returns the top-ranked job
2. **Extract Job Skills (LLM)** — uses `gpt-4.1-mini` to extract concrete technical skills from the job description
3. **Extract Resume Skills** — keyword matching against a curated skill list with alias normalization
4. **Compare Skills** — set intersection/difference to identify strengths and gaps
5. **Final Structured Answer** — LLM synthesizes all tool results into a coherent recommendation

---



##  Setup Instructions

### 1. Clone Repo

```bash
git clone https://github.com/your-username/job-search-agent.git
cd job-search-agent
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Add API Key

Create `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

---

### 5. Run the Agent

```bash
python main.py
```

---

##  Tech Stack

* Python
* OpenAI SDK
* REST APIs (Remotive jobs)
* Regex / text processing
* Tool-calling architecture
* `python-dotenv` for environment management

---

##  Author

**Ashu Surana**
Fullstack Developer | AI Enthusiast

* Python | Django | React | AI Applications
* Building intelligent, data-driven systems

