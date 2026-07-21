import streamlit as st
from utils.db import save_candidate, load_data, init_db
from utils.job_catalog import get_all_jobs
from utils.parser import extract_text_from_pdf, calculate_fit_score

init_db()

st.set_page_config(page_title="AuraHire | Talent Ecosystem", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, #111827 0%, #030712 100%);
        color: #f3f4f6;
    }
    .job-card-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 15px;
        backdrop-filter: blur(12px);
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white; border: none; border-radius: 10px; font-weight: 600;
        padding: 0.5rem 1rem;
    }
    .tracker-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #6366f1;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    .form-container {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #6366f1;
        padding: 25px;
        border-radius: 14px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ AuraHire Talent Ecosystem")
st.markdown("### Next-Generation Career & Talent Screening Platform")

# --- STATUS TRACKER AT THE TOP ---
st.markdown("""
    <div class="tracker-box">
        <h3 style="color: #818cf8; margin-bottom: 5px;">🔐 Candidate Status Tracker</h3>
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 10px;">Enter your Candidate ID or Email below to check your HR approval status and assigned interview schedule.</p>
    </div>
""", unsafe_allow_html=True)

check_id = st.text_input("Enter Candidate ID / Email for Status Check:")
if check_id.strip():
    data = load_data()
    cand = next((c for c in data.get("candidates", []) if str(c.get("id")) == str(check_id.strip())), None)
    if cand:
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.8); padding: 18px; border-radius: 12px; border: 1px solid #4f46e5; margin-bottom: 25px;">
                <p style="margin: 3px 0;"><b>Name:</b> {cand.get('name')}</p>
                <p style="margin: 3px 0;"><b>Role:</b> {cand.get('role')}</p>
                <p style="margin: 3px 0;"><b>Status:</b> {cand.get('status')}</p>
                <p style="margin: 3px 0;"><b>HR Approved:</b> {'Yes ✅' if cand.get('approved') else 'Pending ⏳'}</p>
                <p style="margin: 3px 0;"><b>Interview Slot:</b> {cand.get('interview_slot', 'Not Assigned Yet')}</p>
            </div>
        """, unsafe_allow_html=True)
        if cand.get('approved') and cand.get('interview_slot'):
            st.success("🎉 You are cleared! Navigate to the **Candidate Exam** page to take your assessment.")
            if st.button("🚀 Proceed to Candidate Assessment Console", type="primary"):
                st.session_state["user_role"] = "Applicant"
                st.session_state["applicant_id"] = cand.get("id")
                st.switch_page("pages/2_Candidate_Exam.py")
    else:
        st.warning("No record found matching this ID.")

st.markdown("---")

if "selected_job" not in st.session_state:
    st.session_state.selected_job = None

# --- EXPLORE OPEN ROLES & INLINE APPLICATION ---
st.subheader("🔍 Explore Open Roles")
search_query = st.text_input("Search Roles", placeholder="Type a role name or technology...")

jobs = get_all_jobs()

filtered_jobs = [j for j in jobs if search_query.lower() in j["title"].lower() or search_query.lower() in j["dept"].lower()] if search_query else jobs

for job in filtered_jobs:
    with st.container():
        st.markdown(f"""
            <div class="job-card-container">
                <h4 style="color: #818cf8; margin-bottom: 5px;">{job['title']}</h4>
                <p style="color: #9ca3af; font-size: 13px;"><b>Dept:</b> {job['dept']} &nbsp;|&nbsp; <b>Type:</b> {job['type']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Toggle application form directly underneath the clicked job card
        if st.button(f"Apply for {job['title']}", key=f"btn_{job['title']}"):
            if st.session_state.selected_job == job['title']:
                st.session_state.selected_job = None # Toggle close if already open
            else:
                st.session_state.selected_job = job['title']

        # Render application form inline right below this specific job card if selected
        if st.session_state.selected_job == job['title']:
            st.markdown(f"""
                <div class="form-container">
                    <h3 style="color: #a855f7; margin-bottom: 15px;">📝 Submit Application for: {job['title']}</h3>
            """, unsafe_allow_html=True)
            
            with st.form(f"application_form_{job['title']}"):
                col1, col2 = st.columns(2)
                with col1:
                    candidate_id = st.text_input("Candidate Email / Unique ID", placeholder="e.g. cand-kenny or email@example.com")
                    full_name = st.text_input("Full Name", placeholder="e.g. Kenny Smith")
                with col2:
                    applied_role = st.text_input("Target Role", value=job['title'], disabled=True)
                    
                resume_file = st.file_uploader("Upload Resume (PDF Format)", type=["pdf"])
                
                submitted = st.form_submit_button("🚀 Submit Application")
                if submitted:
                    if candidate_id.strip() and full_name.strip() and resume_file:
                        score = 85.0
                        try:
                            resume_text = extract_text_from_pdf(resume_file)
                            score, _, _ = calculate_fit_score(resume_text, f"Requirements for {job['title']}")
                        except Exception:
                            score = 85.0
                            
                        save_candidate(
                            candidate_id=candidate_id.strip(),
                            name=full_name.strip(),
                            role=job['title'],
                            score=score,
                            status="Pending",
                            approved=False
                        )
                        st.session_state["user_role"] = "Applicant"
                        st.session_state["applicant_id"] = candidate_id.strip()
                        st.session_state["applicant_name"] = full_name.strip()
                        st.success("Application successfully registered! Track your clearance on the Candidate Status Tracker above.")
                        st.session_state.selected_job = None
                    else:
                        st.error("Please fill in all details and upload your resume.")
            
            st.markdown("</div>", unsafe_allow_html=True)
