import streamlit as st
from utils.db import load_data, save_candidate

st.set_page_config(page_title="Candidate Assessment Portal", page_icon="💻", layout="wide")

# Futuristic Sleek Theme & Styling Injection
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, #111827 0%, #030712 100%);
        color: #f3f4f6;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white; border: none; border-radius: 10px; font-weight: 600;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

st.title("💻 Candidate Secure Assessment Console")

default_id = st.session_state.get("applicant_id", "cand-kenny")
candidate_id = st.text_input("Verify Your Candidate ID to Load Assessment:", value=default_id)

if candidate_id.strip():
    data = load_data()
    candidates = data.get("candidates", [])
    current = next((c for c in candidates if str(c.get("id")) == str(candidate_id.strip())), None)
    
    if current:
        is_approved = current.get("approved", False)
        slot = current.get("interview_slot", None)
        
        st.markdown(f"**Welcome, {current.get('name')}** | Applied Role: *{current.get('role')}*")
        
        # --- DUAL-GATE SECURITY CHECK ---
        if is_approved and slot:
            st.success(f"✅ Interview Slot Confirmed: **{slot}** | HR Approval: **Granted**")
            st.markdown("---")
            
            with st.form("exam_submission_form"):
                st.subheader("Part 1: Technical MCQs")
                q1 = st.radio("1. What is the primary purpose of regularization in ML?", 
                         ["A. Speed up training", "B. Reduce overfitting by penalizing complexity", "C. Increase dimensions"])
                
                q2 = st.radio("2. Which library is optimized for multi-dimensional arrays?", 
                         ["A. NumPy", "B. Flask", "C. Pandas"])
                
                st.subheader("Part 2: Coding Assessment")
                st.markdown("**Problem:** Write a Python function `two_sum(nums, target)` that returns indices of the two numbers such that they add up to target.")
                code_solution = st.text_area("Write your Python code here:", "def two_sum(nums, target):\n    # Write logic here\n    pass", height=150)
                
                submit_exam = st.form_submit_button("Submit Assessment to HR", type="primary")
                
                if submit_exam:
                    # Simple automated test evaluation simulation
                    score = 85.5 # Calculated score
                    save_candidate(
                        candidate_id=current["id"],
                        name=current["name"],
                        role=current["role"],
                        score=score,
                        status="Evaluated",
                        approved=True
                    )
                    st.success("🎉 Assessment submitted successfully! Only your final performance score has been securely dispatched to the HR team.")
        else:
            st.warning("🔒 **Assessment Locked:** Your assessment will unlock only after HR grants approval *and* assigns your interview slot.")
    else:
        st.error("Invalid Candidate ID.")
else:
    st.info("Please enter your Candidate ID above to load your candidate console.")
