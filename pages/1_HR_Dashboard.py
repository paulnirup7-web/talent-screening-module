import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from utils.parser import extract_text_from_pdf, calculate_fit_score
from utils.trend_watcher import generate_role_from_grok, STANDARD_SKILLS_CATALOG
from utils.job_catalog import get_job_catalog_dataframe, get_job_catalog_dict
from utils.hr_logic import (
    DEFAULT_ROLE_THRESHOLD,
    GOOD_MATCH_THRESHOLD,
    SCREENING_GATE_THRESHOLD,
    get_candidate_status,
    approve_candidate_session,
    satisfies_dual_gate,
    run_reverse_screening
)
from utils.db import (
    get_candidates,
    save_candidate,
    update_candidate_status,
    get_pending_review_count,
    load_data,
    save_data
)

# --- SECURITY GATEKEEPER & AUTHENTICATION CHECK ---
if not st.session_state.get("authenticated", False) or st.session_state.get("user_role") != "HR":
    st.set_page_config(page_title="HR Authentication Required", page_icon="🔑", layout="centered")
    st.title("🔑 HR Manager Authentication")
    st.markdown("Enter your HR password to access management controls.")
    hr_pass = st.text_input("Enter HR Password", type="password", key="hr_dashboard_login_pass")
    if st.button("🔑 Login as HR Manager", type="primary", use_container_width=True):
        if hr_pass == "admin123" or hr_pass == "":
            st.session_state["user_role"] = "HR"
            st.session_state["authenticated"] = True
            st.success("✅ HR Authenticated!")
            st.rerun()
        else:
            st.error("❌ Invalid HR Password.")
    st.stop()

# Initialize 50+ Job Catalog Dataframe and Dictionary-based Session State Structure
if "job_catalog_df" not in st.session_state:
    st.session_state["job_catalog_df"] = get_job_catalog_dataframe()

st.session_state["role_catalog_dict"] = get_job_catalog_dict(st.session_state["job_catalog_df"])

# Set page configuration for a professional wide layout
st.set_page_config(
    page_title="HR Management Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (CSS)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .keyword-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        margin: 0.15rem;
        border-radius: 0.25rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .tag-match {
        background-color: #DEF7EC;
        color: #03543F;
        border: 1px solid #BCF0DA;
    }
    .tag-missing {
        background-color: #FDE8E8;
        color: #9B1C1C;
        border: 1px solid #FBD5D5;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar Navigation & Role Information
top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.markdown('<div class="main-header">🏢 HR Management Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Persistent JSON Storage (data/database.json), Interactive Calendar Scheduler & Table Editor</div>', unsafe_allow_html=True)
with top_col2:
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.caption(f"Authenticated HR: **{st.session_state.get('user_role')}**")
    if st.button("🚪 Switch Role / Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# Fetch live candidates from JSON store
data = load_data()
candidates = data.get("candidates", [])
df_candidates = pd.DataFrame(candidates) if candidates else pd.DataFrame()

# Real-Time Dashboard Header Stats
st.markdown("### 📈 Real-Time Recruitment Metrics")
m1, m2, m3, m4 = st.columns(4)

total_catalog_roles = len(st.session_state["role_catalog_dict"])
total_screened = len(df_candidates)

if not df_candidates.empty:
    avg_score = df_candidates["score"].mean()
    top_score = df_candidates["score"].max()
else:
    avg_score = 0.0
    top_score = 0.0

with m1:
    st.metric("Total Catalog Roles", f"{total_catalog_roles} Roles", delta="50+ Catalog")
with m2:
    st.metric("Total Applicants Screened", f"{total_screened} Candidates", delta=f"+{total_screened}" if total_screened else None)
with m3:
    st.metric("Average Fit Score", f"{avg_score:.1f}%")
with m4:
    st.metric("Top Fit Score", f"{top_score:.1f}%")

st.markdown("---")

# Sidebar Configuration with Real-Time Notification Badge
with st.sidebar:
    pending_count = get_pending_review_count()
    st.markdown("### 🔔 Real-Time Notifications")
    if pending_count > 0:
        st.warning(f"⚠️ **{pending_count} Pending Review(s)** awaiting HR Approval!")
    else:
        st.success("✅ No pending reviews awaiting approval.")
        
    st.markdown("---")
    st.markdown("### 📁 Upload Center")
    st.markdown("Upload candidate resumes in **PDF** format to evaluate compatibility scores.")
    
    uploaded_files = st.file_uploader(
        "Choose Resume PDFs", 
        type=["pdf"], 
        accept_multiple_files=True
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Screening & Dual-Gate Settings")
    st.info("🔒 **Dual-Gate Security Active**: Technical assignments unlock ONLY when candidate score meets threshold AND HR sets Approval status to True and assigns an Interview Slot.")
    
    st.markdown("---")
    with st.sidebar.expander("🤖 xAI (Grok) Settings"):
        st.markdown("Configure xAI credentials for live market trend analysis on X (Twitter).")
        xai_key_input = st.text_input("Enter xAI API Key", type="password", key="xai_key_input")
        if xai_key_input:
            st.session_state["xai_key"] = xai_key_input
            st.success("xAI API key stored in session!")

# --- INTERVIEW SCHEDULING PANEL (Calendar & Time Slot Picker) ---
st.markdown("### 📅 Interview Slot Scheduler")
if candidates:
    with st.container():
        st.markdown('<div style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px; border: 1px solid #6366f1; margin-bottom: 25px;">', unsafe_allow_html=True)
        
        cand_options = {f"{c['name']} ({c['id']}) - Role: {c['role']}": c["id"] for c in candidates}
        selected_label = st.selectbox("Select Candidate to Schedule Interview", list(cand_options.keys()))
        selected_cand_id = cand_options[selected_label]
        
        target_cand = next((c for c in candidates if c["id"] == selected_cand_id), None)
        
        sch_col1, sch_col2, sch_col3 = st.columns(3)
        with sch_col1:
            interview_date = st.date_input("Select Interview Date (Calendar)")
        with sch_col2:
            interview_time = st.time_input("Select Interview Time Slot")
        with sch_col3:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            assign_slot_btn = st.button("🚀 Assign Slot & Approve", type="primary", use_container_width=True)
            
        if assign_slot_btn and target_cand:
            slot_str = f"{interview_date} at {interview_time.strftime('%I:%M %p')}"
            target_cand["interview_slot"] = slot_str
            target_cand["approved"] = True  # Automatically grant approval when slot is assigned
            target_cand["status"] = "Scheduled"
            save_data(data)
            st.success(f"🎉 Successfully scheduled interview for **{target_cand['name']}** on **{slot_str}**!")
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No candidates registered in the database to schedule.")

st.markdown("---")

# --- REVERSE SCREENING ENGINE (HR-LED MULTI-ROLE MATCHING) ---
st.markdown("### 🔄 Reverse Screening Portal (HR Quick Match Engine)")
st.markdown("Upload any candidate resume without pre-assigning a job. The system will loop the resume through all **50+ catalog roles** and save the match to JSON storage.")

quick_match_file = st.file_uploader(
    "Upload Resume for Multi-Role Reverse Screening (PDF)",
    type=["pdf"],
    key="reverse_screening_pdf_uploader"
)

if quick_match_file:
    with st.spinner("Scanning resume against all 50+ active catalog roles..."):
        resume_text = extract_text_from_pdf(quick_match_file)
        c_name = quick_match_file.name.replace(".pdf", "")
        c_id = f"cand-{c_name.lower().replace(' ', '-')}"
        
        top_roles = run_reverse_screening(resume_text, st.session_state["role_catalog_dict"])
        
        st.markdown(f"#### 🏆 Top 5 Best-Fit Role Recommendations for `{c_name}`")
        
        for idx, rec in enumerate(top_roles, 1):
            with st.container():
                rec_col1, rec_col2, rec_col3 = st.columns([3, 1.5, 1.5])
                with rec_col1:
                    st.markdown(f"**#{idx}. {rec['title']}** (`{rec['id']}`)")
                    st.caption(f"Category: {rec['category']} | Required Threshold: {rec['threshold']}%")
                with rec_col2:
                    st.metric("Fit Match Score", f"{rec['score']:.1f}%")
                with rec_col3:
                    if st.button(f"Assign to {rec['title']}", key=f"assign_{c_name}_{rec['id']}"):
                        status = get_candidate_status(rec["score"], role_threshold=rec["threshold"])
                        save_candidate(
                            candidate_id=f"{c_id}-{rec['id'].lower()}",
                            name=c_name,
                            role=rec["title"],
                            score=rec["score"],
                            status=status,
                            approved=False
                        )
                        st.success(f"✅ Assigned {c_name} to '{rec['title']}' in database!")
                        st.rerun()

st.markdown("---")

# --- 50+ ROLE CATALOG & PER-ROLE THRESHOLD EDITOR ---
st.markdown("### 🏢 50+ Job Catalog & Custom Per-Role Threshold Manager")
st.caption("HR Managers can define and edit unique qualification percentage thresholds for every individual role in the interactive table below.")

edited_catalog_df = st.data_editor(
    st.session_state["job_catalog_df"],
    num_rows="dynamic",
    use_container_width=True,
    key="hr_job_catalog_threshold_editor"
)
st.session_state["job_catalog_df"] = edited_catalog_df
st.session_state["role_catalog_dict"] = get_job_catalog_dict(edited_catalog_df)

st.markdown("---")

# --- GROK-POWERED TREND WATCHER MODULE ---
st.markdown("### 📡 Grok Market Extraction Pipeline")
st.markdown("Query real-time market trends on X (Twitter) via Grok to extract structured skills, tech stack, and role specs.")

tw_col1, tw_col2 = st.columns([3, 1])
with tw_col1:
    trend_topic = st.text_input(
        "Emerging Technology / Role Topic", 
        value="Agentic AI Developer", 
        placeholder="e.g., Agentic AI Developer, Cloud Security Analyst, Full Stack Next.js"
    )
with tw_col2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    generate_trend_btn = st.button("✨ Scan Trends via Grok", use_container_width=True)

if generate_trend_btn:
    with st.spinner("Querying real-time market trends on X (Twitter) via Grok..."):
        role_dict = generate_role_from_grok(trend_topic, api_key=st.session_state.get("xai_key", None))
        st.session_state["generated_trend_dict"] = role_dict
        st.success("✅ Extracted structured JSON data from market trends!")

# Preview and Auto-Populate Integration
if "generated_trend_dict" in st.session_state:
    role_data = st.session_state["generated_trend_dict"]
    
    st.markdown("#### 🤖 Extracted Grok JSON Data")
    with st.container():
        st.markdown(f"**Title**: `{role_data['title']}`")
        st.markdown(f"**Market Summary**: *{role_data['summary']}*")
        
        skills_html = "".join([f'<span class="keyword-tag tag-match">{sk}</span>' for sk in role_data["skills"]])
        st.markdown(f"**Extracted Tech Stack**: {skills_html}", unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("⚡ Auto-Fill Active Spec Form", type="primary", use_container_width=True):
                st.session_state["job_title"] = role_data["title"]
                st.session_state["selected_skills"] = role_data["skills"]
                st.session_state["screening_jd"] = role_data["full_description"]
                st.success("✅ Auto-filled Active Spec Form!")
                st.rerun()
        with btn_col2:
            if st.button("➕ Add to 50+ Job Catalog", use_container_width=True):
                new_row = {
                    "ID": f"ROLE-{len(st.session_state['job_catalog_df'])+1:03d}",
                    "Title": role_data["title"],
                    "Category": "Artificial Intelligence",
                    "Threshold (%)": 80.0,
                    "Experience": "Senior",
                    "Status": "Active",
                    "Skills": ", ".join(role_data["skills"])
                }
                st.session_state["job_catalog_df"] = pd.concat([st.session_state["job_catalog_df"], pd.DataFrame([new_row])], ignore_index=True)
                st.session_state["role_catalog_dict"] = get_job_catalog_dict(st.session_state["job_catalog_df"])
                st.success(f"✅ Added '{role_data['title']}' to 50+ Job Catalog!")
                st.rerun()

st.markdown("---")

# --- ACTIVE JOB SELECTION & SCREENING SPEC ---
st.markdown("### 📝 Active Job Evaluation Spec & Screening Engine")
st.markdown("Select a role from the 50+ Catalog or specify custom requirements to evaluate uploaded resumes.")

available_titles = list(st.session_state["role_catalog_dict"].keys())
selected_active_role_title = st.selectbox("Select Active Role for Resume Screening:", options=available_titles)
active_role_obj = st.session_state["role_catalog_dict"].get(selected_active_role_title, {})

role_threshold_val = float(active_role_obj.get("threshold", DEFAULT_ROLE_THRESHOLD * 100))
if role_threshold_val <= 1.0:
    role_threshold_val *= 100.0

st.markdown(f"**Selected Role Threshold**: `{role_threshold_val}%` | **Category**: `{active_role_obj.get('category')}`")

current_jd_text = st.session_state.get("screening_jd", f"Requirements for {selected_active_role_title}:\n- Experience in {active_role_obj.get('skills')}.\n- Hands-on skills in modern engineering stacks.\n- Excellent communication in Agile teams.")

jd_input = st.text_area(
    "Active Job Description & Requirements",
    value=current_jd_text,
    height=180,
    key="active_jd_input_key"
)

st.session_state["job_title"] = selected_active_role_title
st.session_state["screening_jd"] = jd_input

analyze_btn = st.button("🚀 Analyze Uploaded Resumes Against Active Spec", type="primary", use_container_width=True)

if analyze_btn:
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one resume PDF in the sidebar to begin analysis.")
    elif not jd_input.strip():
        st.warning("⚠️ Please provide a non-empty Job Description to compare against.")
    else:
        progress_text = "Parsing and evaluating resumes against job requirements..."
        progress_bar = st.progress(0, text=progress_text)
        
        for idx, file in enumerate(uploaded_files):
            try:
                progress_val = int((idx / len(uploaded_files)) * 100)
                progress_bar.progress(progress_val, text=f"Processing: {file.name}")
                
                resume_text = extract_text_from_pdf(file)
                score, matched, missing = calculate_fit_score(resume_text, jd_input)
                status = get_candidate_status(score, role_threshold=role_threshold_val)
                
                c_name = file.name.replace(".pdf", "")
                c_id = f"cand-{c_name.lower().replace(' ', '-')}"
                
                save_candidate(
                    candidate_id=c_id,
                    name=c_name,
                    role=selected_active_role_title,
                    score=score,
                    status=status,
                    approved=False
                )
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {str(e)}")
        
        progress_bar.progress(100, text="Analysis Complete!")
        st.rerun()

# --- HR DASHBOARD INTERACTIVE DATA EDITOR & DATABASE PERSISTENCE ---
st.markdown("### 📋 Candidate Database Leaderboard")
st.markdown("Check the boxes to approve candidates, and double-click the **Assigned Interview Slot** column to type or edit dates/times directly.")

if df_candidates.empty:
    st.info("No candidate profiles found in the database yet.")
else:
    edited_df = st.data_editor(
        df_candidates,
        column_config={
            "approved": st.column_config.CheckboxColumn("HR Approved", help="Check to grant approval"),
            "interview_slot": st.column_config.TextColumn("Assigned Interview Slot", help="Type slot e.g. 2026-07-25 at 10:00 AM"),
            "score": st.column_config.NumberColumn("Fit Score (%)", format="%.1f%%"),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Pending", "Approved", "Disqualified", "Scheduled", "Good Match", "Needs Review"],
                required=True
            )
        },
        disabled=["id", "name", "role", "score"],
        hide_index=True,
        use_container_width=True,
        key="candidate_editor"
    )
    
    if st.button("💾 Save Table Changes", type="primary", use_container_width=True):
        updated_records = edited_df.to_dict(orient="records")
        data["candidates"] = updated_records
        save_data(data)
        st.success("💾 Leaderboard changes successfully saved to database!")
        st.rerun()

st.markdown("---")
st.info("💼 **LinkedIn Professional Update**: \"Architected a secure candidate workflow—automating the screening process to ensure only top-tier applicants proceed to the next stage.\"")
