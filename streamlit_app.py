import streamlit as st
import json
from app.agent import run_agent

st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: #FAFAFA;
}

.stTextInput input, .stTextArea textarea {
    background-color: #262730;
    color: white;
}

.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
}

.job-card {
    background-color: #1E1E2F;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# Page config
st.set_page_config(page_title="AI Job Matcher + Skill Analyzer", layout="centered")

# Title
st.title("AI Job Search and Skill Analyzer")
st.markdown("Analyze your resume against real job requirements using AI.")

# INPUT SECTION
with st.container():
    query = st.text_input(
        " Job Search Query",
        placeholder="e.g. Python AI Engineer, Full Stack Developer"
    )

    resume = st.text_area(
        "📄 Paste Your Resume",
        height=250,
        placeholder="Paste your full resume here..."
    )

analyze = st.button(" Analyze Skills")

# MAIN EXECUTION
if analyze:
    if not query.strip() or not resume.strip():
        st.warning(" Please provide both job query and resume.")
    else:
        with st.spinner("Analyzing jobs and your skills..."):
            result, job = run_agent(query, resume)

        st.success(" Analysis Complete")

        # JOB CARD (LinkedIn Style)
       
        if job:
            st.markdown("##  Job Match")

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {job.get('title', 'N/A')}")
                st.markdown(f"** {job.get('company', 'Unknown')}**")

                st.markdown("####  Description")
                st.write(job.get("description", "No description available."))

                if job.get("url"):
                    st.markdown(f"[🔗 Apply Now]({job['url']})")

            with col2:
                score = job.get("score", 0)
                st.metric("Match Score", score)

               
                st.progress(min(score / 15, 1.0))

                # Match badge
                if score >= 10:
                    st.success(" High Match")
                elif score >= 6:
                    st.warning(" Medium Match")
                else:
                    st.info("Low Match")

        # SKILL ANALYSIS
        
        st.markdown("---")
        st.markdown("##  Skill Analysis")

        if result:
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

        # DEBUG / OPTIONAL (nice touch)
        with st.expander(" Debug Info (Optional)"):
            st.write("Raw Job Data:")
            st.json(job)