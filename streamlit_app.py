import streamlit as st
import json
from html import escape
from app.agent import run_agent
from app.tools import search_jobs
import io
from pypdf import PdfReader

# CONFIG PAGE
st.set_page_config(page_title="AI Job Analyzer", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #f8fafc 0%, #eef4ff 50%, #f8fafc 100%);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 1.8rem;
            padding-bottom: 2rem;
        }

        .hero {
            padding: 1.4rem 1.5rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 60%, #60a5fa 100%);
            color: #ffffff;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 16px 36px rgba(15, 23, 42, 0.16);
        }

        .hero h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .hero p {
            margin: 0.55rem 0 0 0;
            color: rgba(255, 255, 255, 0.92);
            line-height: 1.45;
        }

        .panel-title {
            margin: 0 0 0.35rem 0;
            font-size: 1.05rem;
            font-weight: 700;
            color: #0f172a;
        }

        .panel-copy {
            margin: 0;
            color: #475569;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .score-chip {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            font-weight: 700;
            font-size: 0.8rem;
            border: 1px solid rgba(29, 78, 216, 0.15);
        }

        .job-title {
            margin: 0;
            font-size: 1.3rem;
            font-weight: 700;
            line-height: 1.25;
            color: #0f172a;
        }

        .job-description {
            margin: 0.6rem 0 0.85rem 0;
            font-size: 0.92rem;
            line-height: 1.45;
            color: #334155;
        }

        div[data-testid="stButton"] > button,
        div[data-testid="stLinkButton"] a {
            border-radius: 999px;
            font-weight: 700;
            min-height: 2.5rem;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            border-radius: 14px;
            border: 1px solid rgba(15, 23, 42, 0.15);
            background: rgba(255, 255, 255, 0.96);
        }

        .analysis-box {
            padding: 0.85rem 1rem;
            border-radius: 12px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            margin-bottom: 0.75rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = ""

if "last_uploaded_pdf_sig" not in st.session_state:
    st.session_state["last_uploaded_pdf_sig"] = None

# HELPERS
def get_jobs_only(query):
    try:
        result = search_jobs(query)
        return json.loads(result)
    except:
        return []

def extract_text_from_pdf(uploaded_file):
    try:
        pdf_bytes = uploaded_file.getvalue()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        parts = []

        for page in reader.pages:
            text = (page.extract_text() or "").strip()
            if text:
                parts.append(text)

        return "\n\n".join(parts)
    except Exception:
        return ""

# HEADER
st.markdown(
    """
    <div class="hero">
        <h1>AI Job Search and Skill Analyzer</h1>
        <p>Find jobs, select your best match, and analyze skill gaps before applying.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns(2, gap="large")

# INPUT
with left_col:
    with st.container(border=True):
        st.markdown('<p class="panel-title">Search Setup</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="panel-copy">Enter a role and fetch the top matching jobs.</p>',
            unsafe_allow_html=True,
        )

        query = st.text_input(
            "Job Search Query",
            placeholder="e.g. Python AI Engineer, Full Stack Developer"
        )

        resume_box = st.empty()

        uploaded_resume = st.file_uploader(
            "Upload Resume (PDF)",
            type=["pdf"],
            help="Upload a PDF to auto-fill the resume box."
        )

        if uploaded_resume is None:
            st.session_state["last_uploaded_pdf_sig"] = None
        else:
            current_sig = f"{uploaded_resume.name}:{uploaded_resume.size}"

            if st.session_state["last_uploaded_pdf_sig"] != current_sig:
                extracted = extract_text_from_pdf(uploaded_resume)
                st.session_state["last_uploaded_pdf_sig"] = current_sig

                if extracted.strip():
                    st.session_state["resume_text"] = extracted
                    st.success("PDF resume loaded into the text box.")
                else:
                    st.warning("Could not extract text from this PDF.")

        resume_box.text_area(
            "Paste Your Resume",
            key="resume_text",
            height=320,
            placeholder="Paste your resume text here..."
        )

        # SEARCH BUTTON
        if st.button("Find Jobs", use_container_width=True):
            if not query.strip():
                st.warning("Please enter a job query")
            else:
                with st.spinner("Fetching jobs..."):
                    jobs = get_jobs_only(query)

                if jobs:
                    st.session_state["jobs"] = jobs
                else:
                    st.error("No jobs found")

        st.caption("Flow: Find Jobs -> Analyze -> Review strengths and skill gaps")

with right_col:
    # SHOW JOB CARDS
    if "jobs" in st.session_state:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Top Job Matches</p>', unsafe_allow_html=True)
            st.markdown(
                '<p class="panel-copy">Pick a role, then run your fit analysis.</p>',
                unsafe_allow_html=True,
            )

            jobs = st.session_state["jobs"]

            for i, job in enumerate(jobs):
                job_title = escape(str(job.get("title") or "Untitled Role"))
                description = str(job.get("description") or "")
                short_description = description[:130].strip()

                if len(description) > 130:
                    short_description += "..."

                with st.container(border=True):
                    title_col, score_col = st.columns([5, 2])
                    with title_col:
                        st.markdown(
                            f"<p class='job-title'>{job_title}</p>",
                            unsafe_allow_html=True,
                        )
                        st.caption(job.get("company"))
                    with score_col:
                        st.markdown(
                            f"<span class='score-chip'>Score: {job.get('score')}</span>",
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        f"<div class='job-description'>{escape(short_description)}</div>",
                        unsafe_allow_html=True,
                    )

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        if st.button("Analyze", key=f"analyze_{i}", use_container_width=True):
                            st.session_state["selected_job"] = job

                    with col2:
                        if job.get("url"):
                            st.link_button("Apply", job["url"], use_container_width=True)

if "selected_job" in st.session_state:
    job = st.session_state["selected_job"]
    resume_text = st.session_state.get("resume_text", "")

    with st.container(border=True):
        st.subheader("Skill Analysis")
        st.markdown('<div class="analysis-box">Selected role analysis appears below.</div>', unsafe_allow_html=True)

        if not resume_text.strip():
            st.warning("Please paste your resume")
        else:
            with st.spinner("Analyzing selected job..."):
                result, _ = run_agent(
                    f"{job['title']} {job['description']}",
                    resume_text
                )

            st.success("Analysis Complete")

            sections = result.split("\n\n")

            for section in sections:
                if "JOB SUMMARY" in section:
                    st.markdown("### Job Summary")
                elif "CANDIDATE STRENGTHS" in section:
                    st.markdown("### Strengths")
                elif "SKILL GAPS" in section:
                    st.markdown("### Skill Gaps")
                elif "RECOMMENDATIONS" in section:
                    st.markdown("### Recommendations")

                st.markdown(section)