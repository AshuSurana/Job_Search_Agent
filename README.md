# Autonomous Job Search Copilot

An AI-powered job search application that helps candidates discover relevant jobs, evaluate how well their resume matches role requirements, and identify the skills they need to improve.

Built with Python, Streamlit, and the OpenAI API, this project demonstrates how LLMs can work alongside APIs and rule-based logic to solve a practical real-world problem in career discovery and skill evaluation.

## Why This Project Matters

Job seekers often know what roles they want, but it is harder to understand how well their current profile fits a job and what specific skills are missing. This project addresses that gap by turning a job search into a guided decision-making workflow.

Instead of only listing jobs, the application helps users answer:

- Which jobs match my interests?
- Which of my existing skills align with this role?
- What am I missing?
- What should I improve next?

## Key Features

- Search jobs based on a user-defined query
- Rank jobs using a custom scoring approach
- Extract technical skills from job descriptions using an LLM
- Detect skills from resume text using keyword matching and alias normalization
- Compare candidate skills against job requirements
- Generate a structured analysis with:
  - job summary
  - candidate strengths
  - skill gaps
  - recommendations
- Support both a CLI workflow and a Streamlit web interface

## How It Works

### 1. Job Search
The application fetches job listings from an external jobs API and scores them based on keyword relevance, role alignment, and skill-related matches.

### 2. Job Skill Extraction
Once a job is selected, the system uses an OpenAI model to extract concrete technical skills from the job description.

### 3. Resume Skill Extraction
The candidate's resume is analyzed using a curated skill list and alias mapping to identify known technologies and tools.

### 4. Skill Comparison
The extracted job skills and resume skills are compared to identify overlaps and missing requirements.

### 5. Final AI Analysis
The agent produces a structured response with a clear summary of the role, the candidate's strengths, skill gaps, and actionable recommendations.

## Tech Stack

- Python
- Streamlit
- OpenAI API
- dotenv for environment configuration

## What This Project Demonstrates

This project highlights practical software engineering and AI application skills, including:

- API integration
- prompt design
- LLM tool-calling workflows
- stateful agent orchestration
- text processing and skill extraction
- Streamlit application development
- designing AI systems for real user problems

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/job-search-agent.git
cd job-search-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add environment variables

Create a `.env` file and add:

```env
OPENAI_API_KEY=your_api_key_here
```

### 5. Run the app

For the CLI version:

```bash
python main.py
```

For the Streamlit version:

```bash
streamlit run streamlit_app.py
```

## Author

Ashu Surana  
Full Stack Developer | AI Enthusiast

Focused on building practical applications that combine software engineering with AI to solve real-world problems.

