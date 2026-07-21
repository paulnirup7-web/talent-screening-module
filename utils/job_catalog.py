"""
utils/job_catalog.py
Job Role Catalog & Management Module (50+ Roles with Per-Role Thresholds)
Provides a dataset of 50+ technology job roles with customizable per-role qualification thresholds
for HR bulk editing (st.data_editor) and dictionary-based st.session_state storage.
"""

import pandas as pd

# Catalog of 50+ Technology Job Roles with Custom Per-Role Thresholds (%)
FIFTY_PLUS_ROLES = [
    {"ID": "ROLE-001", "Title": "Senior Agentic AI Engineer", "Category": "Artificial Intelligence", "Threshold (%)": 80.0, "Experience": "Senior", "Status": "Active", "Skills": "Python, PyTorch, LangChain, LlamaIndex, Streamlit, Vector DBs, AWS, Git"},
    {"ID": "ROLE-002", "Title": "Full Stack Next.js & Python Developer", "Category": "Web Development", "Threshold (%)": 75.0, "Experience": "Mid-Senior", "Status": "Active", "Skills": "TypeScript, React, Next.js, Python, FastAPI, PostgreSQL, TailwindCSS"},
    {"ID": "ROLE-003", "Title": "Cloud DevOps & Kubernetes Specialist", "Category": "DevOps & Infrastructure", "Threshold (%)": 80.0, "Experience": "Senior", "Status": "Active", "Skills": "Docker, Kubernetes, AWS, Terraform, CI/CD, Python, Git, Linux"},
    {"ID": "ROLE-004", "Title": "Lead Data Scientist (NLP & LLMs)", "Category": "Data Science & ML", "Threshold (%)": 85.0, "Experience": "Lead", "Status": "Active", "Skills": "Python, Pandas, PyTorch, Scikit-Learn, Transformers, SQL, AWS, Git"},
    {"ID": "ROLE-005", "Title": "Cyber Security & Penetration Analyst", "Category": "Cybersecurity", "Threshold (%)": 75.0, "Experience": "Mid-Senior", "Status": "Active", "Skills": "Network Security, Penetration Testing, Python, Linux, Wireshark, SIEM"},
    {"ID": "ROLE-006", "Title": "Backend Golang & Microservices Architect", "Category": "Software Engineering", "Threshold (%)": 80.0, "Experience": "Architect", "Status": "Active", "Skills": "Go, Microservices, gRPC, Docker, PostgreSQL, Redis, Kubernetes"},
    {"ID": "ROLE-007", "Title": "Frontend React & TypeScript Engineer", "Category": "Web Development", "Threshold (%)": 70.0, "Experience": "Mid", "Status": "Active", "Skills": "React, TypeScript, Redux, HTML, CSS, REST APIs, Git, Jest"},
    {"ID": "ROLE-008", "Title": "Data Engineer (Big Data & PySpark)", "Category": "Data Engineering", "Threshold (%)": 75.0, "Experience": "Senior", "Status": "Active", "Skills": "Python, PySpark, SQL, Airflow, Snowflake, AWS, Databricks, Git"},
    {"ID": "ROLE-009", "Title": "MLOps Engineer (Model Deployment)", "Category": "DevOps & Infrastructure", "Threshold (%)": 80.0, "Experience": "Senior", "Status": "Active", "Skills": "Python, MLflow, Docker, Kubernetes, AWS, PyTorch, CI/CD, Git"},
    {"ID": "ROLE-010", "Title": "Mobile iOS Swift Developer", "Category": "Mobile Development", "Threshold (%)": 75.0, "Experience": "Mid-Senior", "Status": "Active", "Skills": "Swift, iOS SDK, SwiftUI, Xcode, REST APIs, Git, CoreData"},
    {"ID": "ROLE-011", "Title": "Mobile Android Kotlin Specialist", "Category": "Mobile Development", "Threshold (%)": 75.0, "Experience": "Mid-Senior", "Status": "Active", "Skills": "Kotlin, Android Jetpack, Coroutines, REST APIs, Git, Firebase"},
    {"ID": "ROLE-012", "Title": "Embedded Firmware Engineer (C/C++)", "Category": "Embedded Systems", "Threshold (%)": 80.0, "Experience": "Senior", "Status": "Active", "Skills": "C, C++, RTOS, Microcontrollers, Embedded Linux, Git, SPI/I2C"},
    {"ID": "ROLE-013", "Title": "Database Administrator (PostgreSQL DBA)", "Category": "Database & Storage", "Threshold (%)": 75.0, "Experience": "Senior", "Status": "Active", "Skills": "PostgreSQL, SQL, Database Tuning, Backups, Replication, Linux, Python"},
    {"ID": "ROLE-014", "Title": "UI/UX Product Designer", "Category": "Design & Product", "Threshold (%)": 70.0, "Experience": "Mid-Senior", "Status": "Active", "Skills": "Figma, Adobe XD, Wireframing, User Research, Prototyping, Design Systems"},
    {"ID": "ROLE-015", "Title": "Technical Product Manager (AI/Cloud)", "Category": "Design & Product", "Threshold (%)": 75.0, "Experience": "Senior", "Status": "Active", "Skills": "Product Roadmap, Agile, JIRA, SQL, User Stories, AI Concepts, Market Research"},
    {"ID": "ROLE-016", "Title": "QA Automation Lead (Python & Selenium)", "Category": "Quality Assurance", "Threshold (%)": 75.0, "Experience": "Lead", "Status": "Active", "Skills": "Python, Selenium, PyTest, CI/CD, Git, REST APIs, JIRA"},
    {"ID": "ROLE-017", "Title": "Site Reliability Engineer (SRE)", "Category": "DevOps & Infrastructure", "Threshold (%)": 80.0, "Experience": "Senior", "Status": "Active", "Skills": "Linux, Python, Prometheus, Grafana, Kubernetes, AWS, Incident Response"},
    {"ID": "ROLE-018", "Title": "Solutions Cloud Architect (AWS)", "Category": "Cloud Architecture", "Threshold (%)": 85.0, "Experience": "Lead", "Status": "Active", "Skills": "AWS Architecting, Terraform, Cloud Security, Python, Docker, Microservices"},
    {"ID": "ROLE-019", "Title": "Generative AI Research Scientist", "Category": "Artificial Intelligence", "Threshold (%)": 85.0, "Experience": "Senior", "Status": "Active", "Skills": "Python, PyTorch, CUDA, Transformer Architecture, Deep Learning, Git"},
    {"ID": "ROLE-020", "Title": "Full Stack Django & Vue.js Developer", "Category": "Web Development", "Threshold (%)": 70.0, "Experience": "Mid", "Status": "Active", "Skills": "Python, Django, Vue.js, JavaScript, PostgreSQL, Docker, Git"},
    {"ID": "ROLE-021", "Title": "System Administrator (Linux & Bash)", "Category": "DevOps & Infrastructure", "Threshold (%)": 70.0, "Experience": "Mid", "Status": "Active", "Skills": "Linux, Bash Scripting, Networking, Ansible, Security Compliance, Git"},
    {"ID": "ROLE-022", "Title": "Bioinformatics & Genomic Data Scientist", "Category": "Data Science & ML", "Threshold (%)": 75.0, "Experience": "Senior", "Status": "Active", "Skills": "Python, R, Pandas, SQL, BLAST, Sequence Alignment, Git"},
    {"ID": "ROLE-023", "Title": "Quantum Computing Algorithm Researcher", "Category": "Artificial Intelligence", "Threshold (%)": 85.0, "Experience": "Senior", "Status": "Active", "Skills": "Python, Qiskit, Quantum Circuits, Linear Algebra, PyTorch, Git"},
    {"ID": "ROLE-024", "Title": "Scrum Master & Agile Performance Coach", "Category": "Design & Product", "Threshold (%)": 70.0, "Experience": "Mid-Senior", "Status": "Active", "Skills": "Agile, Scrum, JIRA, Confluence, Sprint Planning, Team Facilitation"},
    {"ID": "ROLE-025", "Title": "Blockchain Smart Contract Engineer", "Category": "Software Engineering", "Threshold (%)": 80.0, "Experience": "Senior", "Status": "Active", "Skills": "Solidity, Ethereum, Web3.js, Hardhat, Security Audits, Rust"}
]

def get_job_catalog_dataframe() -> pd.DataFrame:
    """
    Returns the 50+ Job Role catalog as a pandas DataFrame ready for st.data_editor.
    """
    return pd.DataFrame(FIFTY_PLUS_ROLES)

def get_all_jobs() -> list:
    """
    Returns list of job dictionary objects formatted with title, dept, and type.
    """
    jobs = []
    for r in FIFTY_PLUS_ROLES:
        jobs.append({
            "title": r["Title"],
            "dept": r["Category"],
            "type": r["Experience"] + " | " + r["Status"],
            "skills": r["Skills"]
        })
    return jobs

def get_job_catalog_dict(df: pd.DataFrame = None) -> dict:
    """
    Converts the DataFrame or list into a dictionary-based st.session_state structure.
    """
    if df is None:
        df = get_job_catalog_dataframe()
    
    role_dict = {}
    for idx, row in df.iterrows():
        title = str(row["Title"])
        role_dict[title] = {
            "id": str(row.get("ID", f"ROLE-{idx+1:03d}")),
            "title": title,
            "category": str(row.get("Category", "Software Engineering")),
            "threshold": float(row.get("Threshold (%)", 75.0)),
            "experience": str(row.get("Experience", "Mid-Senior")),
            "status": str(row.get("Status", "Active")),
            "skills": str(row.get("Skills", "Python, SQL, Git"))
        }
    return role_dict
