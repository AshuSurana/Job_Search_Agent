import streamlit as st
import json
import pandas as pd
import altair as alt
import re
from html import escape
from app.agent import run_agent, run_selected_job_analysis, generate_cover_letter
from app.tools import search_jobs, fetch_job_from_url
import io
from pypdf import PdfReader

# CONFIG PAGE
st.set_page_config(page_title="AI Job Matcher & Analyzer", layout="wide")

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: radial-gradient(circle at top right, #eef2ff, #f8fafc);
        }

        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
        }

        /* Glassmorphic Cards */
        div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            padding: 1.5rem;
        }

        .hero {
            padding: 2.5rem 2rem;
            border-radius: 20px;
            background: #d1fae5 !important;
            color: #065f46 !important;
            margin-bottom: 2rem;
            text-align: center;
        }

        .hero h1 {
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            color: #064e3b !important;
        }

        .job-card {
            border-radius: 16px;
            background: white;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }

        .job-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
            border-color: #3b82f6;
        }

        /* Skill Pills */
        .skill-pill {
            display: inline-block;
            padding: 0.35rem 0.85rem;
            border-radius: 99px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 0.25rem;
            border: 1px solid transparent;
        }
        
        .pill-matched {
            background: #ecfdf5;
            color: #059669;
            border-color: #10b98133;
        }
        
        .pill-missing {
            background: #fef2f2;
            color: #dc2626;
            border-color: #ef444433;
        }

        .pill-extra {
            background: #eff6ff;
            color: #1d4ed8;
            border-color: #3b82f633;
        }

        /* Unified Button & Highlight Theme */
        div[data-testid="stButton"] button, 
        div[data-testid="stFileUploader"] button {
            background-color: #00a35e !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stButton"] button:hover,
        div[data-testid="stFileUploader"] button:hover {
            background-color: #008a50 !important;
            box-shadow: 0 4px 12px rgba(0, 163, 94, 0.2) !important;
        }

        /* Force Tabs to Green */
        button[data-testid="stTab"] p {
            color: #64748b !important;
        }

        button[data-testid="stTab"][aria-selected="true"] {
            border-bottom-color: #00a35e !important;
        }

        button[data-testid="stTab"][aria-selected="true"] p {
            color: #00a35e !important;
            font-weight: 700 !important;
        }

        /* Highlight Text */
        .highlight {
            color: #00a35e !important;
            font-weight: 700 !important;
        }

        .tab-container {
            position: relative;
            margin-bottom: 1rem;
        }

        .tab-card {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            transition: all 0.2s ease;
            background: #f8fafc;
            display: flex;
            align-items: center;
            gap: 1.2rem;
            height: 90px;
            pointer-events: none;
        }

        .tab-card-active {
            background: #f0f5ff !important;
            border-bottom: 3px solid #2563eb !important;
            border-color: #d1d5db;
        }

        .tab-icon {
            background: #e2e8f0;
            color: #475569;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            flex-shrink: 0;
        }

        .tab-card-active .tab-icon {
            background: #cbdcfc;
            color: #2563eb;
        }

        .tab-content h4 {
            margin: 0;
            color: #1e293b;
            font-size: 1.15rem;
            font-weight: 700;
        }

        .tab-content p {
            margin: 0.1rem 0 0 0;
            color: #64748b;
            font-size: 0.88rem;
            line-height: 1.2;
        }

        /* MODERN RADIO TABS (STREAMLIT 1.55.0) - AGGRESSIVE FIX */
        div[data-testid="stRadio"],
        div[data-testid="stRadio"] > div {
            width: 100% !important;
            max-width: none !important;
        }

        /* Hide EVERYTHING inside stRadio except the group */
        div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {
            display: none !important;
        }

        div[data-testid="stRadio"] [role="radiogroup"] {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important; /* Force 50/50 split */
            gap: 1.5rem !important;
            width: 100% !important;
            max-width: none !important;
        }

        /* THE CARD LABEL - TRUE FULL WIDTH */
        div[data-testid="stRadio"] [role="radiogroup"] label {
            background-color: white !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 0.8rem 1.8rem !important;
            height: 80px !important;
            cursor: pointer !important;
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 1.5rem !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
            transition: all 0.2s ease !important;
            position: relative !important;
            margin: 0 !important;
            width: 100% !important;
        }

        /* KILL THE RED DOT (Aggressive) */
        div[data-testid="stRadio"] [role="radiogroup"] label div[data-testid="stRadioButtonDot"],
        div[data-testid="stRadio"] [role="radiogroup"] label div:first-child:not([data-testid="stMarkdownContainer"]) {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
            position: absolute !important;
        }

        /* ICON CIRCLES */
        div[data-testid="stRadio"] [role="radiogroup"] label::before {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 48px;
            background: #f1f5f9;
            border-radius: 50%;
            font-size: 1.5rem;
            flex-shrink: 0;
            content: "🔍";
            order: -1;
        }
        div[data-testid="stRadio"] [role="radiogroup"] label:nth-child(2)::before {
            content: "🔗";
        }

        /* Selected State */
        div[data-testid="stRadio"] [role="radiogroup"] label[data-checked="true"],
        div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
            background-color: #ecfdf5 !important;
            border: 1px solid #d1fae5 !important;
            border-bottom: 4px solid #00a35e !important;
        }
        
        div[data-testid="stRadio"] [role="radiogroup"] label[data-checked="true"]::before,
        div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked)::before {
            background: white !important;
        }

        /* Text Layout */
        div[data-testid="stRadio"] [role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            color: #1e293b !important;
            margin: 0 !important;
        }

        div[data-testid="stRadio"] [role="radiogroup"] label div[data-testid="stWidgetCaption"] {
            font-size: 0.88rem !important;
            color: #64748b !important;
            margin-top: 0 !important;
        }

        /* GLOBAL BUTTON STYLE */
        .stApp div[data-testid="stButton"] button {
            background-color: #00a35e !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 0.6rem 2rem !important;
        }

        /* TEXT INPUT FOCUS COLOR (ULTRA AGGRESSIVE) */
        div[data-testid="stTextInput"] div,
        div[data-testid="stTextArea"] div,
        div[data-baseweb="input"],
        div[data-baseweb="textarea"] {
            border-color: #e2e8f0 !important; /* Neutral gray default */
        }

        div[data-testid="stTextInput"] div:focus-within,
        div[data-testid="stTextArea"] div:focus-within,
        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="textarea"]:focus-within,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div {
            border-color: #00a35e !important; /* Signature Green */
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #00a35e !important;
            box-shadow: 0 0 0 2px rgba(0, 163, 94, 0.2) !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            border-radius: 12px !important;
        }

        /* TIP & NOTIFICATION STYLING (PERFECT NAVBAR MATCH) */
        div[data-testid="stNotification"],
        div[data-testid="stAlert"],
        div[data-testid="stAlert"] > div {
            background-color: #d1fae5 !important;
            color: #065f46 !important;
            border: none !important;
            border-radius: 12px !important;
        }
        
        div[data-testid="stNotification"] svg,
        div[data-testid="stAlert"] svg {
            fill: #00a35e !important;
        }

        /* Force color on all text children */
        div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
        div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] span,
        div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] li {
            color: #065f46 !important;
            font-weight: 600 !important;
        }

        /* Banner Styling */
        .top-banner {
            background-color: #d1fae5;
            color: #065f46;
            padding: 0.5rem 1rem;
            text-align: center;
            font-size: 0.85rem;
            font-weight: 600;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }

        /* Metric Styling */
        [data-testid="stMetricValue"] {
            color: #00a35e !important;
            font-weight: 800 !important;
        }
        
        [data-testid="stMetricLabel"] p {
            color: #475569 !important;
            font-weight: 600 !important;
        }

        /* Spinner & Progress Bar */
        div[data-testid="stSpinner"] > div {
            border-top-color: #00a35e !important;
        }

        div[data-testid="stProgress"] > div > div > div {
            background-color: #00a35e !important;
        }

        /* Hide Default Streamlit Header */
        header {
            visibility: hidden;
            height: 0;
        }

        .nav-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background: #ecfdf5;
            border-bottom: 1px solid #d1fae5;
            display: flex;
            align-items: center;
            padding: 0 5rem;
            z-index: 999999;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        }

        .nav-logo {
            font-size: 1.5rem;
            font-weight: 800;
            color: #00a35e;
            letter-spacing: -0.5px;
        }

        /* Adjust main content for fixed nav */
        div[data-testid="stAppViewContainer"] .main .block-container {
            padding-top: 8rem !important;
        }
        
        .hero {
            margin-top: 2rem !important;
            padding: 1.5rem 2rem;
            border-radius: 20px;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: #ffffff;
            margin-bottom: 1.5rem;
            text-align: center;
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

def render_nav_bar():
    st.markdown(
        """
        <div class="nav-bar">
            <div class="nav-logo">CareerPulse</div>
            <div style="margin-left: auto; color: #065f46; font-size: 0.9rem; font-weight: 600; background: #d1fae5; padding: 0.4rem 1rem; border-radius: 20px;">
                ✨ AI-Powered Skill Matching
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_skill_pills(skills, status="matched"):
    if status == "matched": class_name = "pill-matched"
    elif status == "missing": class_name = "pill-missing"
    else: class_name = "pill-extra"
    
    html = ""
    for s in sorted(skills):
        html += f'<span class="skill-pill {class_name}">{s.capitalize()}</span>'
    return html

def render_skill_chart(resume_skills, job_skills, ai_stats=None):
    if ai_stats and (ai_stats.get("matched_skills") or ai_stats.get("missing_skills")):
        # Use AI-driven comparison for accuracy
        m_set = set([s.lower() for s in ai_stats.get("matched_skills", [])])
        g_set = set([s.lower() for s in ai_stats.get("missing_skills", [])])
        e_set = set([s.lower() for s in ai_stats.get("extra_skills", [])])
        
        data = []
        for s in m_set: data.append({"Skill": s.capitalize(), "Status": "Matched"})
        for s in g_set: data.append({"Skill": s.capitalize(), "Status": "Missing"})
        for s in e_set: data.append({"Skill": s.capitalize(), "Status": "Extra"})
    else:
        # Fallback to robust set logic
        def clean(s_str):
            c = s_str.replace("\n", ",").replace("•", ",").replace("*", ",")
            res = set()
            for s in c.split(","):
                s = s.strip().lower()
                if s:
                    s = re.sub(r'^[\-\d\.\)\s]+', '', s).strip()
                    if s: res.add(s)
            return res

        r_set = clean(resume_skills)
        j_set = clean(job_skills)
        
        all_skills = r_set.union(j_set)
        data = []
        for s in all_skills:
            data.append({
                "Skill": s.capitalize(),
                "Status": "Matched" if s in r_set and s in j_set else ("Missing" if s in j_set else "Extra")
            })
    
    if not data:
        st.info("No concrete skills identified for charting.")
        return

    df = pd.DataFrame(data)
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('count():Q', title='Count'),
        y=alt.Y('Status:N', title=None),
        color=alt.Color('Status:N', scale=alt.Scale(domain=['Matched', 'Missing', 'Extra'], range=['#10b981', '#ef4444', '#60a5fa']))
    ).properties(height=150)
    
    st.altair_chart(chart, use_container_width=True)
    
    # Calculate match pct based on AI stats if available
    if ai_stats and (ai_stats.get("matched_skills") or ai_stats.get("missing_skills")):
        m = len(ai_stats.get("matched_skills", []))
        total = m + len(ai_stats.get("missing_skills", []))
        match_pct = (m / total * 100) if total > 0 else 0
    else:
        r_set = clean(resume_skills)
        j_set = clean(job_skills)
        match_pct = (len(r_set.intersection(j_set)) / len(j_set) * 100) if j_set else 0
        
    st.metric("Overall Skill Match", f"{int(match_pct)}%")
    
    # --- COVER LETTER BUTTON (SMART LOGIC) ---
    st.divider()
    if "cl_draft" not in st.session_state:
        st.session_state["cl_draft"] = ""
    
    btn_label = "✍️ Draft Cover Letter (High Match!)" if match_pct >= 75 else "✍️ Generate Draft Cover Letter"
    btn_type = "primary" if match_pct >= 75 else "secondary"
    
    if st.button(btn_label, use_container_width=True, type=btn_type):
        with st.spinner("AI is crafting your tailored cover letter..."):
            draft = generate_cover_letter(st.session_state["selected_job"], st.session_state["resume_text"])
            st.session_state["cl_draft"] = draft
            st.rerun()

    if st.session_state["cl_draft"]:
        with st.container(border=True):
            st.markdown("### 📝 AI Generated Cover Letter")
            st.caption("You can edit the draft below to add your personal touch.")
            edited_cl = st.text_area("Interactive Editor", value=st.session_state["cl_draft"], height=400, key="cl_editor")
            st.session_state["cl_draft"] = edited_cl
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state["cl_draft"] = ""
                    st.rerun()
            with c2:
                st.download_button("📥 Download Text", data=edited_cl, file_name="Cover_Letter.txt", use_container_width=True)

# SIDEBAR: RESUME MANAGEMENT
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resume.png", width=60)
    st.markdown("### My Career Profile")
    st.caption("Manage your resume and profile data here.")
    
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
                st.success("Resume loaded!")
            else:
                st.warning("Could not extract text.")

    st.text_area(
        "Edit Resume Text",
        key="resume_text",
        height=350,
        placeholder="Paste your resume text here..."
    )
    st.divider()
    st.info("💡 Tip: A well-formatted resume leads to better matching.")

# RENDER NAV BAR (Separated for easy removal)
render_nav_bar()

# HEADER
st.markdown(
    """
    <div class="hero">
        <h2>Job Search and Skill Analyzer</h2>
        <p style="font-size: 1.1rem; opacity: 0.9;">Find jobs, select your best match, and analyze skill gaps before applying.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- INITIALIZE STATE & PARAMS ---
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "search"

# Check for query params if supported
try:
    params = st.experimental_get_query_params()
    if "tab" in params:
        st.session_state["active_tab"] = params["tab"][0]
except:
    pass

# --- JOB SELECTION SECTION (CENTERED) ---
with st.container():
    st.markdown("#### Resume-to-Job Alignment")
    
    # Map selection back to options list
    tab_options = ["Search Jobs", "Analyze URL"]
    current_index = 0 if st.session_state["active_tab"] == "search" else 1

    # Use radio with captions for modern Streamlit 1.55.0
    tab_selection = st.radio(
        "Job Selection",
        options=tab_options,
        captions=["AI-powered job discovery", "Instant fit analysis"],
        index=current_index,
        horizontal=True,
        label_visibility="collapsed",
        key="nav_radio",
        on_change=lambda: st.session_state.update({"active_tab": "search" if "Search" in st.session_state.nav_radio else "url"})
    )
    
    if st.session_state["active_tab"] == "search":
        st.markdown("##### 🔍 Search New Jobs")
        # Search input and button in a compact row
        sc1, sc2 = st.columns([4, 1])
        with sc1:
            query = st.text_input("What role are you looking for?", placeholder="e.g. Senior Python Developer", key="main_search_query")
        with sc2:
            st.write(" ") # Spacer
            st.write(" ") # Spacer
            if st.button("Find Jobs", use_container_width=True):
                if query.strip():
                    with st.spinner("Searching Remotive API..."):
                        jobs_list = get_jobs_only(query)
                        if jobs_list:
                            st.session_state["jobs"] = jobs_list
                        else:
                            st.error("No jobs found for that query.")
                else:
                    st.warning("Please enter a query.")

        # Show Job Results in a Horizontal Grid
        if "jobs" in st.session_state:
            st.markdown("#### 📋 Select a role to analyze:")
            jobs_to_show = st.session_state["jobs"][:3]
            job_cols = st.columns(len(jobs_to_show))
            
            for i, job in enumerate(jobs_to_show):
                with job_cols[i]:
                    with st.container(border=True):
                        st.markdown(f"**{job['title']}**")
                        st.caption(f"🏢 {job['company']}")
                        if st.button("Analyze This Role", key=f"sel_job_{i}", use_container_width=True):
                            st.session_state["selected_job"] = job
                            st.success(f"Selected: {job['title']}")

    else:
        st.markdown("##### 🔗 Analyze Specific URL")
        job_url = st.text_input("Paste Job URL (e.g., LinkedIn, Indeed, etc.)", placeholder="https://...")
        if st.button("Fetch & Analyze", use_container_width=True):
            if job_url:
                with st.spinner("Scraping Job Data..."):
                    job_data = fetch_job_from_url(job_url)
                    if job_data:
                        # Proceed to analysis logic directly
                        st.session_state["selected_job"] = job_data
                        st.success("Job data fetched successfully!")
                    else:
                        st.error("Could not extract job data. Try another URL.")
            else:
                st.warning("Please paste a URL.")
    
    st.caption("Flow: Find/Paste Job -> Select -> Review Analysis below")

if "selected_job" in st.session_state:
    job = st.session_state["selected_job"]
    resume_text = st.session_state.get("resume_text", "")

    st.divider()
    
    if not resume_text.strip():
        st.warning("⚠️ Please provide your resume in the sidebar to begin the analysis.")
    else:
        with st.spinner("Running Deep Analysis..."):
            result, data = run_selected_job_analysis(job, resume_text)
        
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Fit Analysis", "💡 Strategy"])
        
        with tab1:
            col_chart, col_stats = st.columns([2, 1])
            with col_chart:
                render_skill_chart(data["resume_skills"], data["job_skills"], data.get("stats"))
            with col_stats:
                st.markdown("### Match Summary")
                stats = data.get("stats", {})
                m_list = stats.get("matched_skills", [])
                g_list = stats.get("missing_skills", [])
                j_count = len(m_list) + len(g_list)
                m_count = len(m_list)
                
                if j_count == 0:
                    j_count = len([s for s in data["job_skills"].replace("\n", ",").split(",") if s.strip()])
                    m_count = len([s for s in data["comparison"].split("Strengths:")[1].split("Gaps:")[0].split(",") if s.strip() and "none" not in s.lower()])

                st.info(f"**Required Skills:** {j_count}")
                st.success(f"**Matching Skills:** {m_count}")
        
        with tab2:
            st.markdown('### <span class="highlight"> Technical Fit Analysis</span>', unsafe_allow_html=True)
            
            # Extract lists for pills
            stats = data.get("stats", {})
            matched = stats.get("matched_skills", [])
            missing = stats.get("missing_skills", [])
            extra = stats.get("extra_skills", [])
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.success("✅ **Matched Skills**")
                if matched:
                    st.markdown(render_skill_pills(matched, "matched"), unsafe_allow_html=True)
                else:
                    st.caption("No direct matches found.")
            
            with c2:
                st.error("🚨 **Missing Skills**")
                if missing:
                    st.markdown(render_skill_pills(missing, "missing"), unsafe_allow_html=True)
                else:
                    st.caption("No significant gaps identified!")

            with c3:
                st.info("💎 **Extra Strengths**")
                if extra:
                    st.markdown(render_skill_pills(extra, "extra"), unsafe_allow_html=True)
                else:
                    st.caption("No additional skills noted.")
            
            st.divider()
            
            sections = result.split("\n\n")
            for section in sections:
                if "CANDIDATE STRENGTHS" in section:
                    with st.expander("💪 Detailed Strengths", expanded=True):
                        st.markdown(section.replace("CANDIDATE STRENGTHS:", ""))
                elif "SKILL GAPS" in section:
                    with st.expander("🚩 Detailed Gap Analysis", expanded=True):
                        st.markdown(section.replace("SKILL GAPS:", ""))

        with tab3:
            st.markdown('### <span class="highlight"> Strategic Recommendations</span>', unsafe_allow_html=True)
            sections = result.split("\n\n")
            for section in sections:
                if "RECOMMENDATIONS" in section:
                    st.info(section.replace("RECOMMENDATIONS:", ""))
                elif "JOB SUMMARY" in section:
                    with st.expander("📝 Job Context"):
                        st.markdown(section)
            
            st.divider()
            st.markdown('### <span class="highlight"> Next Steps</span>', unsafe_allow_html=True)
            st.info("💡 Your cover letter draft is available in the **Dashboard** tab once generated.")

        with st.expander("🔍 Debug: Raw Data"):
            c1, c2, c3 = st.columns(3)
            c1.text_area("Job Skills", data["job_skills"], height=100)
            c2.text_area("Resume Skills", data["resume_skills"], height=100)
            c3.json(data.get("stats", {}))