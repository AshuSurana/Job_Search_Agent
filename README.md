# Autonomous Job Search Copilot (AI Agent)

An intelligent **agentic AI system** built using Python and OpenAI SDK that automates job search, analyzes candidate skills, and identifies gaps against real-world job requirements.

---

## Overview

This project demonstrates a **multi-step autonomous agent** that:

* Searches real-time job listings
* Extracts required skills from job descriptions
* Extracts skills from a candidate’s resume
* Compares both using structured logic
* Generates actionable recommendations

The system uses **tool-calling + reasoning loop**, simulating how modern AI agents operate.

---

##  Key Features

*  **Job Search Integration**

  * Fetches jobs using public APIs (Remotive)

*  **Multi-step Agent Workflow**

  * Tool-based execution (search → extract → compare → recommend)

*  **Skill Extraction Engine**

  * From job descriptions
  * From resume text

*  **Skill Gap Analysis**

  * Identifies strengths vs missing skills


*  **Low-cost AI usage**

  * Uses lightweight model (`gpt-4.1-mini`)

---

##  How It Works

### Agent Workflow

1. **Search Jobs**
2. **Extract Job Skills**
3. **Extract Resume Skills**
4. **Compare Skills**
5. **Generate Final Insights**

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

---

##  Author

**Ashu Surana**
Fullstack Developer | AI Enthusiast

* Python | Django | React | AI Applications
* Building intelligent, data-driven systems

