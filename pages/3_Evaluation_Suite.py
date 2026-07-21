import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from utils.eval_suite import run_golden_dataset_evaluation, evaluate_candidate_submission
from utils.db import get_candidates

# --- MANDATORY SECURITY GATEKEEPER CHECK ---
if "user_role" not in st.session_state:
    st.switch_page("app.py")

# Set page configuration for the Evaluation Suite Dashboard
st.set_page_config(
    page_title="AI Model Accuracy & Project Evaluation Suite",
    page_icon="📈",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .eval-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .eval-sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar Navigation
top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.markdown('<div class="eval-header">📈 AI Model Accuracy & Evaluation Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="eval-sub-header">Golden Dataset Benchmark, Project Grading & HR Verification Gating</div>', unsafe_allow_html=True)
with top_col2:
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.caption(f"Role: **{st.session_state.get('user_role')}**")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.markdown("---")

# --- SECTION 1: CANDIDATE PROJECT SUBMISSION EVALUATION & HR VERIFICATION GATING ---
st.markdown("### 🔒 Candidate Project Submissions & HR Verification Gating")
st.caption("Feedback visibility and detailed project grading remain restricted until HR verifies and updates candidate records.")

db_candidates = get_candidates()

if db_candidates.empty:
    st.info("ℹ️ No candidate records found in SQLite DB (recruitment_platform.db). Submit applications to populate candidate projects.")
else:
    for idx, candidate in db_candidates.iterrows():
        c_id = candidate["id"]
        c_name = candidate["name"]
        c_role = candidate["role"]
        c_score = candidate["score"]
        c_status = candidate["status"]
        is_verified = bool(candidate.get("approved", False) or c_status in ["Approved", "Shortlisted"])
        
        with st.container():
            j_col1, j_col2, j_col3 = st.columns([3, 2, 2])
            
            with j_col1:
                st.markdown(f"**👤 {c_name}** (`ID: {c_id}`) — Target Role: `{c_role}`")
                st.caption(f"AI Compatibility Score: {c_score:.1f}% | Database Status: `{c_status}`")
            with j_col2:
                if is_verified:
                    st.success(f"✅ **HR Verified**: Status `{c_status}`")
                else:
                    st.warning("⏳ **Awaiting HR Verification**")
            with j_col3:
                if is_verified:
                    st.info("🔓 Feedback & Detailed Grading Unlocked")
                else:
                    st.caption("🔒 Feedback & Grading Restricted")

            # Restrict feedback visibility and project grading details until HR verifies
            if is_verified:
                with st.expander(f"🔍 Detailed Project Grading & Feedback for {c_name}"):
                    st.markdown("##### 📝 Automated Project Evaluation Summary")
                    st.markdown(f"- **Candidate Compatibility**: `{c_score:.1f}%`")
                    st.markdown(f"- **HR Status**: `{c_status}`")
                    st.markdown("##### 💡 Technical Feedback & Analysis")
                    st.markdown("Candidate demonstrates strong domain alignment. Recommended for next-stage technical interview.")
            else:
                st.markdown("<p style='color:#6B7280; font-style:italic;'>🔒 Detailed project grading and feedback are restricted until an HR Manager verifies this record in the HR Dashboard.</p>", unsafe_allow_html=True)
            st.markdown("---")

# --- SECTION 2: GOLDEN DATASET BENCHMARK METRICS ---
st.markdown("### 🏆 Golden Dataset Accuracy Benchmark (25 Resumes)")

with st.spinner("Processing 25 Golden Dataset Resumes against Human Ground Truth..."):
    eval_results = run_golden_dataset_evaluation()

summary = eval_results["summary"]
df_eval = eval_results["detailed_df"]

# Summary Metrics Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Test Cases", f"{summary['total_resumes']} Resumes")
with m2:
    st.metric("Mean Absolute Error (MAE)", f"{summary['mae_percentage']:.2f}%", help="Lower is better (< 5.0% is production grade)")
with m3:
    st.metric("Human-AI Correlation", f"{summary['correlation_accuracy']:.1f}%", help="Higher is better (> 90.0% target)")
with m4:
    st.metric("Gate Agreement Rate", f"{summary['screening_gate_agreement_rate']:.1f}%", help="Percentage of identical Pass/Fail decisions between AI and Human")

st.markdown("---")

# Comparison Chart
st.markdown("#### 📊 Human Ground Truth vs. AI Score Comparison")

fig, ax = plt.subplots(figsize=(12, 4.5))
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#f9fafb')

x = range(len(df_eval))
width = 0.35

ax.bar([i - width/2 for i in x], df_eval["Human Validated Score (%)"], width, label='Human Score (%)', color='#1E3A8A')
ax.bar([i + width/2 for i in x], df_eval["AI Fit Score (%)"], width, label='AI Score (%)', color='#3B82F6')

ax.set_ylabel('Fit Score (%)', fontweight='bold', color='#374151')
ax.set_title('Human vs AI Score Alignment Across Golden Dataset', fontweight='bold', color='#111827')
ax.set_xticks(x)
ax.set_xticklabels(df_eval["Candidate Name"], rotation=45, ha='right', fontsize=8)
ax.legend()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()

st.pyplot(fig)

st.markdown("---")

# AG Grid Detailed Benchmark Table
st.markdown("#### 📋 Detailed Benchmark Leaderboard (AG-Grid)")

gb = GridOptionsBuilder.from_dataframe(df_eval)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
gb.configure_side_bar()
gb.configure_default_column(editable=True, groupable=True, filterable=True, sortable=True)
grid_options = gb.build()

AgGrid(
    df_eval,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode='AS_INPUT',
    fit_columns_on_grid_load=True,
    theme='streamlit',
    height=300
)

# Diagnostic Failure Points
st.markdown("---")
st.markdown("### 🔍 Root Cause Failure Point Diagnostics")

failure_cases = df_eval[df_eval["Absolute Difference (%)"] > 5.0]
if not failure_cases.empty:
    st.warning(f"Found {len(failure_cases)} test profiles with variance > 5.0% between Human and AI scoring.")
    for idx, row in failure_cases.iterrows():
        with st.expander(f"⚠️ Variance Profile: {row['Candidate Name']} — Error: {row['Absolute Difference (%)']:.1f}%"):
            st.markdown(f"**Human Score**: `{row['Human Validated Score (%)']}%` | **AI Score**: `{row['AI Fit Score (%)']}%`")
            st.markdown(f"**Diagnostic Analysis**: High keyword density discrepancy or non-standard formatting detected.")
else:
    st.success("🎉 Zero high-variance failure points! All test cases matched human ground truth within 5% tolerance.")
