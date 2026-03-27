import streamlit as st
import json
from app.agent import run_agent
from app.tools import search_jobs

# Helper: Fetch jobs only
def get_jobs_only(query):
    try:
        result = search_jobs(query)
        return json.loads(result)
    except:
        return []

# Page config
st.set_page_config(page_title="AI Job Skill Analyzer", layout="centered")

st.header(" AI Job Search and Skill Gap Analyzer")
st.markdown("Find jobs → Click → Analyze skill gaps")

# INPUT
query = st.text_input(
    " Job Search Query",
    placeholder="e.g. Python AI Engineer, Full Stack Developer"
)

resume = st.text_area(
    "📄 Paste Your Resume",
    height=250
)

analyze = st.button(" Find Jobs")

# STEP 1: FETCH JOBS
if analyze:
    if not query.strip():
        st.warning("Please enter a job query")
    else:
        with st.spinner("Fetching jobs..."):
            jobs = get_jobs_only(query)

        if jobs:
            st.session_state["jobs"] = jobs
        else:
            st.error("No jobs found")

# STEP 2: SHOW JOBS
if "jobs" in st.session_state:
    st.markdown("##  Top Job Matches")

    for i, job in enumerate(st.session_state["jobs"]):
        with st.container():
            st.markdown(f"""
            ### {job.get('title')}
            ** {job.get('company')}**

            {job.get('description')}
            """)

            col1, col2 = st.columns([3, 1])

            with col1:
                if job.get("url"):
                    st.markdown(f"[🔗 Apply Now]({job['url']})")

            with col2:
                st.metric("Score", job.get("score", 0))

            #  SELECT BUTTON
            if st.button("Analyze This Job", key=f"btn_{i}"):
                st.session_state["selected_job"] = job

# STEP 3: ANALYZE SELECTED JOB
if "selected_job" in st.session_state:
    job = st.session_state["selected_job"]

    st.markdown("---")
    st.markdown("##  Skill Analysis")

    if not resume.strip():
        st.warning(" Please paste your resume to analyze.")
    else:
        with st.spinner("Analyzing selected job..."):
            result, _ = run_agent(
                f"{job['title']} {job['description']}",
                resume
            )

        # DISPLAY RESULTS
       
        sections = result.split("\n\n")

        for section in sections:
            if "JOB SUMMARY" in section:
                st.markdown("###  Job Summary")
            elif "CANDIDATE STRENGTHS" in section:
                st.markdown("###  Strengths")
            elif "SKILL GAPS" in section:
                st.markdown("###  Skill Gaps")
            elif "RECOMMENDATIONS" in section:
                st.markdown("###  Recommendations")

            st.markdown(section)