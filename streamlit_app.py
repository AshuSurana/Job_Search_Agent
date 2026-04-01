import streamlit as st
import json
from app.agent import run_agent
from app.tools import search_jobs

# CONFIG PAGE
st.set_page_config(page_title="AI Job Analyzer", layout="centered")

# HELPERS
def get_jobs_only(query):
    try:
        result = search_jobs(query)
        return json.loads(result)
    except:
        return []

# HEADER
st.header(" AI Job Search and Skill Analyzer")
st.markdown("Find jobs → Select → Analyze skill gaps")

# INPUT
query = st.text_input(
    " Job Search Query",
    placeholder="e.g. Python AI Engineer, Full Stack Developer"
)

resume = st.text_area(
    "📄 Paste Your Resume",
    height=220
)

# SEARCH BUTTON
if st.button(" Find Jobs"):
    if not query.strip():
        st.warning("Please enter a job query")
    else:
        with st.spinner("Fetching jobs..."):
            jobs = get_jobs_only(query)

        if jobs:
            st.session_state["jobs"] = jobs
        else:
            st.error("No jobs found")

# SHOW JOB CARDS
if "jobs" in st.session_state:
    st.markdown("##  Top Job Matches")

    jobs = st.session_state["jobs"]

    for i, job in enumerate(jobs):

        with st.container():
            st.markdown(f"###  {job.get('title')}")
            st.markdown(f" **{job.get('company')}**")
            st.caption(f"⭐ Score: {job.get('score')}")

            st.write(job.get("description")[:200] + "...")

            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button(" Analyze", key=f"analyze_{i}"):
                    st.session_state["selected_job"] = job

            with col2:
                if job.get("url"):
                    st.link_button(" Apply", job["url"])

        st.divider()

# ANALYSIS SECTION
if "selected_job" in st.session_state:
    job = st.session_state["selected_job"]

    st.markdown("---")
    st.subheader(" Skill Analysis")

    if not resume.strip():
        st.warning(" Please paste your resume")
    else:
        with st.spinner("Analyzing selected job..."):
            result, _ = run_agent(
                f"{job['title']} {job['description']}",
                resume
            )

        st.success(" Analysis Complete")

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